import unittest
from typing import cast

from waves_gateway.common import DuplicateAttemptListTriggerError, DuplicateAttemptListIDError
from waves_gateway.model import TransactionAttemptList
from waves_gateway.storage import TransactionAttemptListStorage
from unittest.mock import patch, MagicMock


class TransactionAttemptListStorageTest(unittest.TestCase):
    @patch.multiple(TransactionAttemptListStorage, __abstractmethods__=set())  # type: ignore
    def setUp(self):
        self._storage = TransactionAttemptListStorage()

    def test_safely_save_trigger_exists(self):
        with patch.multiple(
                self._storage,
                trigger_exists=MagicMock(),
                attempt_list_id_exists=MagicMock(),
                save_attempt_list=MagicMock()):
            mock_attempt_list = cast(TransactionAttemptList, MagicMock())

            self._storage.trigger_exists.return_value = True
            self._storage.attempt_list_id_exists.return_value = False

            with self.assertRaises(DuplicateAttemptListTriggerError):
                self._storage.safely_save_attempt_list(mock_attempt_list)

    def test_safely_save_attempt_list_id_exists(self):
        with patch.multiple(
                self._storage,
                trigger_exists=MagicMock(),
                attempt_list_id_exists=MagicMock(),
                save_attempt_list=MagicMock()):
            mock_attempt_list = cast(TransactionAttemptList, MagicMock())

            self._storage.trigger_exists.return_value = False
            self._storage.attempt_list_id_exists.return_value = True

            with self.assertRaises(DuplicateAttemptListIDError):
                self._storage.safely_save_attempt_list(mock_attempt_list)

    def test_safely_save_success(self):
        with patch.multiple(
                self._storage,
                trigger_exists=MagicMock(),
                attempt_list_id_exists=MagicMock(),
                save_attempt_list=MagicMock()):
            mock_attempt_list = cast(TransactionAttemptList, MagicMock())

            self._storage.trigger_exists.return_value = False
            self._storage.attempt_list_id_exists.return_value = False

            self._storage.safely_save_attempt_list(mock_attempt_list)

            self._storage.save_attempt_list.assert_called_once_with(mock_attempt_list)
