from logging import Logger
from typing import cast
from unittest import TestCase
from unittest.mock import MagicMock

from waves_gateway.model import Transaction, TransactionReceiver, PollingState
from waves_gateway.service import TransactionPollingService, ChainQueryService, TransactionConsumer
from waves_gateway.storage import BlockHeightStorageProxy, PollingStateStorageProxy


class TransactionPollingServiceSpec(TestCase):
    def _mock_filter_transaction(self, transaction: Transaction):
        return self._gateway_managed_address_receiver in transaction.receivers

    def _apply_filter_transaction_mock(self):
        self._transaction_consumer.filter_transaction.side_effect = self._mock_filter_transaction

    def setUp(self):
        self._gateway_managed_address_receiver = TransactionReceiver("734968234", 832645)

        self._chain_query_service = MagicMock()
        self._logger = MagicMock()
        self._max_handle_transaction_tries = 1
        self._polling_state_storage = MagicMock()
        self._block_height_storage = MagicMock()
        self._transaction_consumer = MagicMock()
        self._min_polling_delay = 0.1
        self._max_polling_delay = 40
        self._last_block_distance = 5
        self._scheduler = MagicMock()
        self._transaction_polling_service = TransactionPollingService(
            chain_query_service=cast(ChainQueryService, self._chain_query_service),
            logger=cast(Logger, self._logger),
            block_height_storage=cast(BlockHeightStorageProxy, self._block_height_storage),
            transaction_consumer=cast(TransactionConsumer, self._transaction_consumer),
            max_handle_transaction_tries=self._max_handle_transaction_tries,
            polling_state_storage=cast(PollingStateStorageProxy, self._polling_state_storage),
            min_polling_delay_s=self._min_polling_delay,
            max_polling_delay_s=self._max_polling_delay,
            last_block_distance=self._last_block_distance)

        self._apply_filter_transaction_mock()

    def test_iteration_do_nothing(self):
        """In the case of a fresh start, the handle_transaction method should not be called."""
        height_of_highest_block = 30
        transaction = Transaction(tx="tx", receivers=[TransactionReceiver("receiver", 6587)])

        self._block_height_storage.get_last_checked_block_height.return_value = None
        self._chain_query_service.get_height_of_highest_block.return_value = height_of_highest_block
        self._chain_query_service.get_transactions_of_block_at_height.return_value = [transaction]
        self._transaction_consumer.filter_transaction.return_value = False
        self._polling_state_storage.get_polling_state.return_value = None

        self._transaction_polling_service._iteration()

        self._transaction_consumer.filter_transaction.assert_not_called()
        self._transaction_consumer.handle_transaction.assert_not_called()
        self._chain_query_service.get_transactions_of_block_at_height.assert_not_called()
        self._block_height_storage.set_last_checked_block_height.assert_called_once_with(height_of_highest_block)

    def test_iteration_handle_one_transaction(self):
        """The TransactionPollingService should process a single transaction that is not filtered."""
        height_of_highest_block = 30
        last_checked_coin_block_height = height_of_highest_block - self._last_block_distance - 1
        transaction = Transaction(tx="tx", receivers=[self._gateway_managed_address_receiver])

        self._block_height_storage.get_last_checked_block_height.return_value = last_checked_coin_block_height
        self._chain_query_service.get_height_of_highest_block.return_value = height_of_highest_block
        self._polling_state_storage.get_polling_state.return_value = None

        def _get_transactions_of_block_at_height(height: int):
            if height == (last_checked_coin_block_height + 1):
                return [transaction]
            else:
                return []

        self._chain_query_service.get_transactions_of_block_at_height.side_effect = _get_transactions_of_block_at_height

        self._transaction_polling_service._iteration()

        self._transaction_consumer.filter_transaction.assert_called_once_with(transaction)
        self._transaction_consumer.handle_transaction.assert_called_once_with(transaction)
        self._chain_query_service.get_transactions_of_block_at_height.assert_called_once_with(
            last_checked_coin_block_height + 1)
        self._block_height_storage.set_last_checked_block_height.assert_called_once_with(
            last_checked_coin_block_height + 1)

    def test_iteration_filter_one_transaction(self):
        """Two transactions were given, one should be filtered and the other one not."""
        height_of_highest_block = 30
        last_checked_coin_block_height = height_of_highest_block - self._last_block_distance - 1
        not_filtered_transaction = Transaction(tx="tx", receivers=[self._gateway_managed_address_receiver])
        filtered_transaction = Transaction(tx="khj", receivers=[TransactionReceiver(address="92634867", amount=3425)])

        self._block_height_storage.get_last_checked_block_height.return_value = last_checked_coin_block_height
        self._chain_query_service.get_height_of_highest_block.return_value = height_of_highest_block
        self._polling_state_storage.get_polling_state.return_value = None

        def _get_transactions_of_block_at_height(height: int):
            if height == (last_checked_coin_block_height + 1):
                return [not_filtered_transaction, filtered_transaction]
            else:
                return []

        self._chain_query_service.get_transactions_of_block_at_height.side_effect = _get_transactions_of_block_at_height

        self._transaction_polling_service._iteration()

        self._transaction_consumer.filter_transaction.assert_any_call(not_filtered_transaction)
        self._transaction_consumer.filter_transaction.assert_any_call(filtered_transaction)
        self._transaction_consumer.handle_transaction.assert_called_once_with(not_filtered_transaction)
        self._chain_query_service.get_transactions_of_block_at_height.assert_called_once_with(
            last_checked_coin_block_height + 1)
        self._block_height_storage.set_last_checked_block_height.assert_called_once_with(
            last_checked_coin_block_height + 1)

    def _mock_real_storage(self):

        self._polling_state_storage._mock_state = PollingState()

        def mock_set_polling_state(state: PollingState):
            self._polling_state_storage._mock_state = state

        def mock_get_polling_state():
            return self._polling_state_storage._mock_state

        self._polling_state_storage.set_polling_state.side_effect = mock_set_polling_state
        self._polling_state_storage.get_polling_state.side_effect = mock_get_polling_state

    def test_skip_transaction_after_too_many_tries(self):
        self._mock_real_storage()

        height_of_highest_block = 30
        last_checked_coin_block_height = height_of_highest_block - self._last_block_distance - 1
        transaction = Transaction(tx="tx", receivers=[self._gateway_managed_address_receiver])

        def _get_transactions_of_block_at_height(height: int):
            if height == (last_checked_coin_block_height + 1):
                return [transaction]
            else:
                return []

        def mock_handle_transaction(tr: Transaction):
            raise KeyError('failed')

        self._block_height_storage.get_last_checked_block_height.return_value = last_checked_coin_block_height
        self._chain_query_service.get_height_of_highest_block.return_value = height_of_highest_block
        self._transaction_consumer.handle_transaction.side_effect = mock_handle_transaction
        self._chain_query_service.get_transactions_of_block_at_height.side_effect = _get_transactions_of_block_at_height

        with self.assertRaises(KeyError):
            self._transaction_polling_service._iteration()

        self._transaction_polling_service._iteration()

        self._transaction_consumer.handle_transaction.assert_called_once_with(transaction)
        self.assertEqual(self._transaction_consumer.filter_transaction.call_count, 2)
