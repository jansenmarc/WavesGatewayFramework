import unittest
from typing import cast
from unittest.mock import MagicMock

from waves_gateway.service import PendingAttemptListSelectorService
from waves_gateway.storage import TransactionAttemptListStorage


class PendingAttemptListSelectorServiceTest(unittest.TestCase):
    def setUp(self):
        self._attempt_list_storage = MagicMock()
        self._attempt_list_selector_service = PendingAttemptListSelectorService(
            cast(TransactionAttemptListStorage, self._attempt_list_storage))

    def test_lock_attempt_list_not_found(self):
        self._attempt_list_storage.find_oldest_pending_attempt_list.return_value = None
        attempt_list = self._attempt_list_selector_service.lock_attempt_list()
        self.assertIsNone(attempt_list)

    def test_lock_attempt_list_found(self):
        mock_attempt_list = MagicMock()

        self._attempt_list_storage.find_oldest_pending_attempt_list.return_value = mock_attempt_list
        res = self._attempt_list_selector_service.lock_attempt_list()
        self.assertEqual(res, mock_attempt_list)
        mock_attempt_list.increment_tries.assert_called_once_with()
        self._attempt_list_storage.update_attempt_list.assert_called_once_with(res)
