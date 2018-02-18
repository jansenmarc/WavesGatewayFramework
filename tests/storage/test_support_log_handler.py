import unittest
from typing import cast
from unittest.mock import MagicMock, patch

from waves_gateway.service.support_log_handler import SupportLogHandler
from waves_gateway.storage import LogStorageService


class LogHandlerTest(unittest.TestCase):
    def setUp(self):
        self._log_storage_service = MagicMock()
        self._logging = MagicMock()
        self._logHandler = SupportLogHandler(log_storage_service=cast(LogStorageService, self._log_storage_service))

    def test_emit(self):
        record = MagicMock()
        record.levelname.return_value = "INFO"

        support_log_handler = MagicMock()

        result = self._logHandler.emit(record)
        support_log_handler._process_info.assert_called()
        # self.assertEqual("", result)


    def test_process_debug(self):
        message = "This is the record message"
        result = self._logHandler._process_debug(message, "Finished block at height")
        self.assertEqual(message, result)


    def test_process_info(self):
        message = "This is the record message"
        result = self._logHandler._process_info(message, "Created new attempt list")
        self.assertEqual(message, result)

        message = "This is the record message"
        result = self._logHandler._process_info(message, "Trying to complete attempt_list")
        self.assertEqual(message, result)

        message = "This is the record message"
        result = self._logHandler._process_info(message, " is already complete")
        self.assertEqual(message, result)

        message = "This is the record message"
        result = self._logHandler._process_info(message, " is complete")
        self.assertEqual(message, result)

        message = "This is the record message"
        result = self._logHandler._process_info(message, ": Transferred")
        self.assertEqual(message, result)

        message = "This is the record message"
        result = self._logHandler._process_info(message, ": Already transferred ")
        self.assertEqual(message, result)



    def test_process_error(self):
        message = "Please check the internet connection."
        result = self._logHandler._process_error(message, "NewConnectionError")
        self.assertEqual(message, result)

        message = "The configuration of the gateway is invalid. Please check the addresses and information in case of their correctness."
        result = self._logHandler._process_error(message, "InvalidConfigError")
        self.assertEqual(message, result)

        message = "Waves node was unable to process request."
        result = self._logHandler._process_error(message, "WavesNodeException")
        self.assertEqual(message, result)

        message = "An attemptlist with this ID already exists."
        result = self._logHandler._process_error(message, "DuplicateAttemptListIDError")
        self.assertEqual(message, result)

        message = "This is the record message"
        result = self._logHandler._process_error(message, "DuplicateSecretError")
        self.assertEqual(message, result)

        message = "An attemptlist with this trigger already exists."
        result = self._logHandler._process_error(message, "DuplicateAttemptListTriggerError")
        self.assertEqual(message, result)

        message = "Attempted to store a mapping for a coin address, but it already exists."
        result = self._logHandler._process_error(message, "DuplicateMappingError")
        self.assertEqual(message, result)

        message = "This is the record message"
        result = self._logHandler._process_error(message, "MappingNotFoundForCoinAddress")
        self.assertEqual(message, result)

        message = "The connection to mongo DB was interrupted. Please check the connection to the mongo DB server."
        result = self._logHandler._process_error(message, "AutoReconnect pymongo")
        self.assertEqual(message, result)

        message = "The connection to mongo DB failed. Please check that the mongo DB server is running."
        result = self._logHandler._process_error(message, "pymongo.errors.ServerSelectionTimeoutError")
        self.assertEqual(message, result)

        message = "The connection to the coin node failed."
        result = self._logHandler._process_error(message, "ConnectionRefusedError")
        self.assertEqual(message, result)