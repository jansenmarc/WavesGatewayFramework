"""
TransactionPollingService
"""

import logging

import time
import gevent
import gevent.pool as pool
import gevent.greenlet as greenlet
from typing import List, Optional

from waves_gateway.common import filter_array
from waves_gateway.model import Transaction, PollingDelayConfig, PollingState, PollingTransactionState
from .transaction_consumer import TransactionConsumer
from waves_gateway.storage import BlockHeightStorageProxy, PollingStateStorageProxy

from .chain_query_service import ChainQueryService


class TransactionPollingService(greenlet.Greenlet):
    """
    The polling service is intended to be spawned once on the start of the application.
    It will reschedule executions of itself in dynamic intervals. It is possible, to cancel
    this service. In this case, no further executions will be scheduled.
    The delay between the executions tries to adjust itself to the time between the creation of new blocks.
    But it will never be less than the min_polling_delay nor more than the max_polling_delay.
    

    It is designed, so that it can be used for both Waves and the custom currency.
    For the particular case, the service must be constructed with the matching parameters
    for the currency.
    """

    def __init__(self, chain_query_service: ChainQueryService, logger: logging.Logger,
                 block_height_storage: BlockHeightStorageProxy, transaction_consumer: TransactionConsumer,
                 polling_state_storage: PollingStateStorageProxy, max_handle_transaction_tries: int,
                 min_polling_delay_s: float, max_polling_delay_s: float, last_block_distance: int) -> None:
        greenlet.Greenlet.__init__(self)

        self._consumer = transaction_consumer
        self._chain_query_service = chain_query_service
        self._logger = logger.getChild(self.__class__.__name__ + "." + transaction_consumer.__class__.__name__)
        self._block_height_storage = block_height_storage
        self._cancelled = False
        self._polling_delay_s = min_polling_delay_s
        self._d_height = 0
        self._min_polling_delay = min_polling_delay_s
        self._max_polling_delay = max_polling_delay_s
        self._last_block_time_s = None  # type: Optional[float]
        self._last_polling_delay = self._polling_delay_s
        self._polling_state_storage = polling_state_storage
        self._max_handle_transaction_tries = max_handle_transaction_tries
        self._polling_state = PollingState()
        self._current_height = None
        self._last_block_distance = last_block_distance

    def _transaction_not_exceeds_tries(self, transaction: Transaction) -> bool:
        """Returns whether the given transaction has failed too often."""
        return self._polling_state.transaction_map[transaction.tx].tries < self._max_handle_transaction_tries

    def _is_transaction_not_already_processed(self, transaction: Transaction) -> bool:
        """Returns whether the transaction has already been successfully processed."""
        transaction_state = self._polling_state.transaction_map[transaction.tx]
        return not transaction_state.ok

    def _should_transaction_be_processed(self, tr: Transaction) -> bool:
        """Summarizes every necessary condition for a transaction to be processed."""
        return self._consumer.filter_transaction(tr) and self._is_transaction_not_already_processed(
            tr) and self._transaction_not_exceeds_tries(tr)

    def _filter_transaction_task(self, transaction: Transaction) -> Optional[Transaction]:
        """Returns the transaction if it should be processed or None otherwise."""
        self._ensure_polling_state_has_transaction(transaction)

        if self._should_transaction_be_processed(transaction):
            return transaction
        else:
            return None

    def _filter_transactions(self, transactions: List[Transaction]) -> List[Transaction]:
        """Filters all transactions in parallel. The results may not have the same order."""
        filter_task_group = pool.Group()
        filter_task_results = filter_task_group.imap_unordered(self._filter_transaction_task, transactions)
        return filter_array(lambda el: el is not None, filter_task_results)

    def cancel(self):
        """Marks the polling as cancelled."""
        self._cancelled = True

    def _log_delay(self):
        self._logger.debug('Sleeping %ss', str(self._polling_delay_s))

    def _apply_delay_border(self):
        if self._polling_delay_s < self._min_polling_delay:
            self._polling_delay_s = self._min_polling_delay

        if self._polling_delay_s > self._max_polling_delay:
            self._polling_delay_s = self._max_polling_delay

    def _adjust_delay_after_not_found_block(self):
        self._polling_delay_s = round(self._polling_delay_s + (self._max_polling_delay * 0.01), 2)
        self._apply_delay_border()

    def _adjust_delay_after_found_block(self):
        if self._last_block_time_s is None:
            self._polling_delay_s = self._min_polling_delay
        elif self._d_height > 1:
            self._polling_delay_s = round(self._polling_delay_s / 2, 2)
        else:
            current_time_s = time.time()
            diff = current_time_s - self._last_block_time_s

            if (self._polling_delay_s + diff) > 0:
                self._polling_delay_s = round((self._polling_delay_s + diff) / 6, 2)

        self._last_block_time_s = time.time()
        self._apply_delay_border()

    def _adjust_delay_after_exception(self):
        self._polling_delay_s = self._max_polling_delay

    def _run(self):
        try:
            while not self._cancelled:
                try:
                    self._iteration()
                except BaseException as ex:
                    self._logger.error(ex, exc_info=True)
                    self._logger.debug("Execution has finished with errors")
                    self._adjust_delay_after_exception()
                finally:
                    self._log_delay()

                gevent.sleep(self._polling_delay_s)
        finally:
            self._logger.info("Cancelled")

    def _ensure_polling_state_has_transaction(self, tr: Transaction):
        if tr.tx not in self._polling_state.transaction_map:
            self._polling_state.transaction_map[tr.tx] = PollingTransactionState()

    def _handle_transaction(self, transaction: Transaction):
        """Calls the transaction_consumer with the given transaction."""
        self._logger.debug("Overhand transaction %s to consumer %s.", transaction.tx, self._consumer.__class__.__name__)

        self._ensure_polling_state_has_transaction(transaction)

        try:
            self._consumer.handle_transaction(transaction)
            self._polling_state.transaction_map[transaction.tx].mark_as_done()
        except BaseException as ex:
            self._polling_state.transaction_map[transaction.tx].increment_tries()
            raise ex

    def _fetch_stored_polling_state(self):
        self._polling_state = self._polling_state_storage.get_polling_state()

        if self._polling_state is None:
            self._polling_state = PollingState()

    def _reset_polling_state(self):
        self._polling_state = PollingState()

    def _update_stored_polling_state(self):
        self._polling_state_storage.set_polling_state(self._polling_state)

    def _handle_transactions(self, transactions: List[Transaction]) -> None:
        for tr in transactions:
            self._handle_transaction(tr)

    def _iteration(self):
        """
        In every execution, it first fetches the last checked block height from storage.
        Along that, it needs the overall height of the chain.
        If the storage is empty, the service only fetches the latest block of the chain.
        If not, which means that there is a last checked block height defined, the service checks all
        blocks from this height to the maximum height.
        When finished with all these blocks, the current maximum height is stored as the last
        checked block height in storage.

        For every block, it fetches all transactions. Those transactions are filtered using the filter
        functionality of the transaction consumer instance.
        Finally, the filtered transactions are each overhanded to the consumer.
        """

        height_of_last_checked_block = self._block_height_storage.get_last_checked_block_height()
        height_of_highest_block = self._chain_query_service.get_height_of_highest_block()

        self._fetch_stored_polling_state()

        if height_of_last_checked_block is None:
            height_of_last_checked_block = height_of_highest_block
            self._block_height_storage.set_last_checked_block_height(height_of_last_checked_block)

        self._d_height = height_of_highest_block - height_of_last_checked_block

        if height_of_last_checked_block >= height_of_highest_block - self._last_block_distance:
            self._logger.debug("Skipping run of transaction polling service as no new blocks are available.")
            self._adjust_delay_after_not_found_block()
            return
        else:
            self._adjust_delay_after_found_block()

        current_height = height_of_last_checked_block + 1

        self._logger.info("Checking block at height %s", str(current_height))

        transactions = self._chain_query_service.get_transactions_of_block_at_height(current_height)
        filtered_transactions = self._filter_transactions(transactions)

        try:
            self._handle_transactions(filtered_transactions)
            self._reset_polling_state()
        finally:
            self._update_stored_polling_state()

        self._block_height_storage.set_last_checked_block_height(current_height)

        self._logger.debug("Finished block at height %s", str(current_height))
