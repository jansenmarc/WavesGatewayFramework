import unittest
from typing import cast
from unittest.mock import MagicMock, patch

import logging

from waves_gateway.service import AttemptListWorker, PendingAttemptListSelectorService, TransactionAttemptListService


class AttemptListWorkerTest(unittest.TestCase):
    def setUp(self):
        self._attempt_list_service = MagicMock()
        self._polling_delay = 0
        self._attempt_list_selector = MagicMock()
        self._logger = MagicMock()
        self._max_polling_delay = 40
        self._min_polling_delay = 0
        self._worker_id = 235

        self._attempt_list_worker = AttemptListWorker(
            attempt_list_selector=cast(PendingAttemptListSelectorService, self._attempt_list_selector),
            attempt_list_service=cast(TransactionAttemptListService, self._attempt_list_service),
            max_polling_delay_s=self._max_polling_delay,
            min_polling_delay_s=self._min_polling_delay,
            logger=cast(logging.Logger, self._logger),
            worker_id=self._worker_id)

    @patch('gevent.sleep', autospec=True)
    def test_run_none(self, sleep: MagicMock):
        self._attempt_list_selector.lock_attempt_list.return_value = None

        self._attempt_list_worker.start()
        self._attempt_list_worker.cancel()
        self._attempt_list_worker.join()

        self.assertEqual(self._attempt_list_selector.lock_attempt_list.call_count, 1)
        sleep.assert_called_once_with(self._min_polling_delay + 1)
        self._attempt_list_selector.release_attempt_list.assert_not_called()

    @patch('gevent.sleep', autospec=True)
    def test_run_found(self, sleep: MagicMock):
        mock_attempt_list = MagicMock()
        self._attempt_list_selector.lock_attempt_list.return_value = mock_attempt_list

        self._attempt_list_worker.start()
        self._attempt_list_worker.cancel()
        self._attempt_list_worker.join()

        self.assertEqual(self._attempt_list_selector.lock_attempt_list.call_count, 1)
        sleep.assert_called_once_with(self._min_polling_delay)
        self._attempt_list_service.continue_transaction_attempt_list.assert_called_once_with(mock_attempt_list)
        self._attempt_list_selector.release_attempt_list.assert_called_once_with(mock_attempt_list)
