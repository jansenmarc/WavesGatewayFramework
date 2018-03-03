"""
MongoKeyValueStorageImpl
"""
from waves_gateway.common import Injectable, KEY_VALUE_STORAGE_COLLECTION
from waves_gateway.model import PollingState
from waves_gateway.serializer import PollingStateSerializer
from waves_gateway.storage.key_value_storage import KeyValueStorage
from pymongo.collection import Collection  # type: ignore
from typing import Optional, Any
from doc_inherit import method_doc_inherit  # type: ignore


@Injectable(deps=[KEY_VALUE_STORAGE_COLLECTION, PollingStateSerializer], provides=KeyValueStorage)
class MongoKeyValueStorageImpl(KeyValueStorage):
    """
    Implements a key value storage with a MongoDB collection.
    """

    _COIN_BLOCK_HEIGHT_KEY = 'coin_block_height'
    _WAVES_BLOCK_HEIGHT_KEY = 'waves_block_height'
    _VALUE_PROPERTY_KEY = 'value'
    _KEY_PROPERTY_KEY = 'key'
    _COIN_POLLING_STATE_KEY = 'coin_polling_state'
    _WAVES_POLLING_STATE_KEY = 'waves_polling_state'

    def _set_value(self, key: str, value: Any) -> None:
        """
        Inserts the key/value pair. Overwrites existing entries.
        """
        query = dict()
        query[MongoKeyValueStorageImpl._KEY_PROPERTY_KEY] = key

        replacement = dict()
        replacement[MongoKeyValueStorageImpl._KEY_PROPERTY_KEY] = key
        replacement[MongoKeyValueStorageImpl._VALUE_PROPERTY_KEY] = value

        self._collection.replace_one(filter=query, replacement=replacement, upsert=True)

    def _get_value(self, key: str) -> Any:
        """
        Returns the value or None if no value was found.
        """
        query = dict()
        query[MongoKeyValueStorageImpl._KEY_PROPERTY_KEY] = key

        query_result = self._collection.find_one(filter=query)

        if query_result is None:
            return None
        else:
            return query_result[MongoKeyValueStorageImpl._VALUE_PROPERTY_KEY]

    @method_doc_inherit
    def set_last_checked_waves_block_height(self, block_height: int) -> None:
        self._set_value(MongoKeyValueStorageImpl._WAVES_BLOCK_HEIGHT_KEY, block_height)

    @method_doc_inherit
    def get_last_checked_waves_block_height(self) -> Optional[int]:
        return self._get_value(MongoKeyValueStorageImpl._WAVES_BLOCK_HEIGHT_KEY)

    def __init__(self, collection: Collection, polling_state_serializer: PollingStateSerializer) -> None:
        self._collection = collection
        self._polling_state_serializer = polling_state_serializer

    @method_doc_inherit
    def set_last_checked_coin_block_height(self, block_height: int) -> None:
        self._set_value(MongoKeyValueStorageImpl._COIN_BLOCK_HEIGHT_KEY, block_height)

    @method_doc_inherit
    def get_last_checked_coin_block_height(self) -> Optional[int]:
        return self._get_value(MongoKeyValueStorageImpl._COIN_BLOCK_HEIGHT_KEY)

    def set_waves_polling_state(self, polling_state: PollingState) -> None:
        self._set_value(MongoKeyValueStorageImpl._WAVES_POLLING_STATE_KEY,
                        self._polling_state_serializer.as_dict(polling_state))

    def get_coin_polling_state(self) -> Optional[PollingState]:
        data = self._get_value(MongoKeyValueStorageImpl._COIN_POLLING_STATE_KEY)

        if data is None:
            return None
        else:
            return self._polling_state_serializer.from_dict(data)

    def get_waves_polling_state(self) -> Optional[PollingState]:
        data = self._get_value(MongoKeyValueStorageImpl._WAVES_POLLING_STATE_KEY)

        if data is None:
            return None
        else:
            return self._polling_state_serializer.from_dict(data)

    def set_coin_polling_state(self, polling_state: PollingState) -> None:
        self._set_value(MongoKeyValueStorageImpl._COIN_POLLING_STATE_KEY,
                        self._polling_state_serializer.as_dict(polling_state))
