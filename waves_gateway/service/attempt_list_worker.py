"""
AttemptListWorker
"""

import gevent.greenlet as greenlet
import logging

from waves_gateway.model import PollingDelayConfig
from .transaction_attempt_list_service import TransactionAttemptListService
from .pending_attempt_list_selector_service import PendingAttemptListSelectorService
import gevent


class AttemptListWorker(greenlet.Greenlet):
    """
    This worker is intended to be spawned once or multiple times at the beginning of the application.
    After that, it will reschedule itself in dynamic intervals.
    The interval can never be less than the min_polling_delay and never be more than the max_polling_delay.
    In every iteration the attempt_list_selector is queried for a pending attempt_list.
    This attempt_list will then be processed by this worker.
    """

    def __init__(self,
                 attempt_list_service: TransactionAttemptListService,
                 attempt_list_selector: PendingAttemptListSelectorService,
                 logger: logging.Logger,
                 worker_id: int,
                 min_polling_delay_s: float = PollingDelayConfig.DEFAULT_MIN_ATTEMPT_LIST_WORKER_DELAY_S,
                 max_polling_delay_s: float = PollingDelayConfig.DEFAULT_MAX_ATTEMPT_LIST_WORKER_DELAY_S) -> None:
        greenlet.Greenlet.__init__(self)
        self._attempt_list_service = attempt_list_service
        self._polling_delay = 0
        self._attempt_list_selector = attempt_list_selector
        self._cancelled = False
        self._logger = logger.getChild(AttemptListWorker.__name__ + '[' + str(worker_id) + ']')
        self._delay_s = 0
        self._min_polling_delay_s = min_polling_delay_s
        self._max_polling_delay_s = max_polling_delay_s
        self._first_run_complete = False

    def _log_delay(self):
        self._logger.debug('Sleeping %ss', str(self._delay_s))

    def _run(self):
        try:
            while not self._cancelled or not self._first_run_complete:
                current = None

                try:
                    self._logger.debug('Trying to get new attempt list')
                    current = self._attempt_list_selector.lock_attempt_list()

                    if current is not None:
                        self._attempt_list_service.continue_transaction_attempt_list(current)
                        self._attempt_list_selector.release_attempt_list(current)
                        current = None
                        self._decrease_polling_delay()
                        self._logger.debug('Successfully finished')
                    else:
                        self._logger.debug('Nothing to do')
                        self._increase_polling_delay()
                except BaseException as ex:
                    self._increase_polling_delay()
                    self._logger.error(ex, exc_info=True)
                    self._logger.debug("Execution has finished with errors")
                finally:
                    if current is not None:
                        self._attempt_list_selector.release_attempt_list(current)

                    self._first_run_complete = True
                    self._log_delay()
                    gevent.sleep(self._delay_s)
        finally:
            self._logger.info("Cancelled")

    def _decrease_polling_delay(self):
        self._delay_s = self._delay_s - 1

        if self._delay_s <= self._min_polling_delay_s:
            self._delay_s = self._min_polling_delay_s

    def _increase_polling_delay(self):
        self._delay_s = self._delay_s + 1

        if self._delay_s >= self._max_polling_delay_s:
            self._delay_s = self._max_polling_delay_s

    def cancel(self):
        self._cancelled = True
