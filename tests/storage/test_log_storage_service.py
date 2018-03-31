import unittest
from typing import cast
from unittest.mock import MagicMock

from pymongo.collection import Collection  # type: ignore

from waves_gateway.storage import LogStorageService


class LogStorageServiceTest(unittest.TestCase):
    def setUp(self):
        self._collection = MagicMock()

        self._log_storage_service = LogStorageService(collection=cast(Collection, self._collection))

    def test_save_message(self):
        message = {
            "date": "2018-03-02T09:12:33",
            "level": "Error",
            "affected_component": "CoinPollingService",
            "message": "abcdefg"
        }
        self._log_storage_service.save_message(message)
        self._collection.insert_one.assert_called_once_with(message)

    def test_get_messages(self):
        self._collection.find.return_value = [{
            "id": "12345",
            "date": "2018-03-02T09:12:33",
            "level": "Error",
            "affected_component": "CoinPollingService",
            "message": "abcdefg"
        }, {
            "id": "12345",
            "date": "2018-03-02T12:12:33",
            "level": "Info",
            "affected_component": "CoinPollingService",
            "message": "Block 123456 has finished"
        }]

        messages = self._log_storage_service.get_messages()

        self._collection.find.assert_called_once_with()
        self.assertEqual(messages, [{
            "id": "12345",
            "date": "2018-03-02T09:12:33",
            "level": "Error",
            "affected_component": "CoinPollingService",
            "message": "abcdefg"
        }, {
            "id": "12345",
            "date": "2018-03-02T12:12:33",
            "level": "Info",
            "affected_component": "CoinPollingService",
            "message": "Block 123456 has finished"
        }])
