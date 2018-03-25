"""
SupportLogHandler
"""
import uuid
from logging import Handler

from waves_gateway.common import Injectable
from waves_gateway.storage.log_storage_service import LogStorageService


@Injectable(deps=[LogStorageService], provides=Handler)
class SupportLogHandler(Handler):
    """
    SupportLogHandler persists logs for support
    """

    def __init__(self, log_storage_service: LogStorageService) -> None:
        Handler.__init__(self)
        self._log_storage_service = log_storage_service

    # will be called from the log handler by logger.info / .error / .debug
    def emit(self, record):
        log_entry = self.format(record)
        datetime = log_entry[1:20]
        level = record.levelname
        affected_component = log_entry.split(" ")[3]
        message = ""

        if level == "INFO":
            message = self._process_info(record.message, log_entry)
        elif level == "DEBUG":
            message = self._process_debug(record.message, log_entry)
        elif level == "ERROR":
            message = self._process_error(record.message, log_entry)
        elif level == "WARNING":
            message = record.message

        if message != "":
            self._log_storage_service.save_message({
                "id": str(uuid.uuid4()),
                "date": datetime,
                "level": level,
                "message": message,
                "affected_component": affected_component
            })

    def _process_debug(self, message: str, log_entry: str):
        if "Finished block at height" in log_entry:
            return message
        else:
            return ""

    def _process_info(self, msg: str, log_entry: str):
        message = ""

        if "Created new attempt list" in log_entry:
            message = msg
        elif "Trying to complete attempt_list" in log_entry:
            message = msg
        elif " is already msg" in log_entry:
            message = msg
        elif " is complete" in log_entry:
            message = msg
        elif ": Transferred" in log_entry:
            message = msg
        elif ": Already transferred " in log_entry:
            message = msg

        return message

    def _process_error(self, msg: str, log_entry: str):
        message = ""
        if "NewConnectionError" in log_entry:
            message = "Please check the internet connection."

        elif "PyWavesError" in log_entry:
            if ("Encountered an unknown exception while trying to perform waves transaction." in log_entry):
                message = "Probleme mit Transaktion"

        elif "InvalidConfigError" in log_entry:
            message = "Please check the Gateway Configuration"

        elif "WavesNodeException" in log_entry:
            message = "Waves node was unable to process request."

        elif "DuplicateAttemptListIDError" in log_entry:
            message = "An attemptlist with this ID already exists."

        elif "DuplicateSecretError" in log_entry:
            message = msg

        elif "MappingNotFoundForCoinAddress" in log_entry:
            message = msg

        elif (("ConnectionRefusedError" in log_entry) or ("AutoReconnect")) and ("pymongo" in log_entry):
            message = "The connection to mongo DB was interrupted. Please check the connection to the mongo DB server."

        elif "pymongo.errors.ServerSelectionTimeoutError" in log_entry:
            message = "The connection to mongo DB failed. Please check that the mongo DB server is running."

        elif "ConnectionRefusedError" in log_entry:
            message = "The connection to the coin node failed."

        return message
