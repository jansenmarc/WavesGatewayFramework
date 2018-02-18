"""
LogStorageService
"""
from pymongo.collection import Collection
from waves_gateway.common import Injectable, GATEWAY_MESSAGE_STORAGE_COLLECTION


@Injectable(deps=[GATEWAY_MESSAGE_STORAGE_COLLECTION])
class LogStorageService:
    """
    LogStorageService for saving logs in mongo db
    """

    def __init__(self, collection: Collection) -> None:
        self._collection = collection

    def save_message(self, message: dict) -> None:
        """
        Save a log message in a mongoDB collection
        """
        self._collection.insert_one(message)

    def get_messages(self):
        """
        Get all log messages from mongoDB
        """
        cursor = self._collection.find()

        res = []

        for each in cursor:
            support_message = {
                "id": each["id"],
                "date": each["date"],
                "level": each["level"],
                "message": each["message"],
                "affected_component": each["affected_component"]
            }
            res.append(support_message)

        return res
