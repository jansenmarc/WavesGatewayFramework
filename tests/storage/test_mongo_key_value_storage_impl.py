import unittest
from unittest.mock import MagicMock, patch
from typing import Any, cast
from waves_gateway.storage.mongo_key_value_storage_impl import MongoKeyValueStorageImpl


class MongoKeyValueStorageImplSpec(unittest.TestCase):
    def setUp(self):
        self._collection = MagicMock()
        self._polling_state_serializer = MagicMock()
        self._key_value_storage = cast(Any,
                                       MongoKeyValueStorageImpl(
                                           collection=self._collection,
                                           polling_state_serializer=self._polling_state_serializer))

    def test_set_value(self):

        key = 'test_key'
        value = 'test_value'

        query = dict()
        query[MongoKeyValueStorageImpl._KEY_PROPERTY_KEY] = key

        replacement = dict()
        replacement[MongoKeyValueStorageImpl._KEY_PROPERTY_KEY] = key
        replacement[MongoKeyValueStorageImpl._VALUE_PROPERTY_KEY] = value

        self._key_value_storage._set_value(key, value)

        self._collection.replace_one.assert_called_once_with(filter=query, replacement=replacement, upsert=True)

    def test_get_value(self):
        key = 'test_key'
        value = 'test_value'

        query = dict()
        query[MongoKeyValueStorageImpl._KEY_PROPERTY_KEY] = key

        entry = dict()
        entry[MongoKeyValueStorageImpl._KEY_PROPERTY_KEY] = key
        entry[MongoKeyValueStorageImpl._VALUE_PROPERTY_KEY] = value

        self._collection.find_one.return_value = entry

        self.assertEqual(value, self._key_value_storage._get_value(key))

        self._collection.find_one.assert_called_once_with(filter=query)

    def test_get_value_none(self):
        key = 'test_key'

        query = dict()
        query[MongoKeyValueStorageImpl._KEY_PROPERTY_KEY] = key

        self._collection.find_one.return_value = None

        self.assertEqual(None, self._key_value_storage._get_value(key))

        self._collection.find_one.assert_called_once_with(filter=query)

    def test_set_last_checked_waves_block_height(self):
        block_height = 2365

        with patch.object(self._key_value_storage, '_set_value'):
            self._key_value_storage.set_last_checked_waves_block_height(block_height)

            self._key_value_storage._set_value.assert_called_once_with(MongoKeyValueStorageImpl._WAVES_BLOCK_HEIGHT_KEY,
                                                                       block_height)

    def test_get_last_checked_waves_block_height(self):
        block_height = 2365

        with patch.object(self._key_value_storage, '_get_value'):
            self._key_value_storage._get_value.return_value = block_height

            self.assertEqual(self._key_value_storage.get_last_checked_waves_block_height(), block_height)

            self._key_value_storage._get_value.assert_called_once_with(MongoKeyValueStorageImpl._WAVES_BLOCK_HEIGHT_KEY)

    def test_set_last_checked_coin_block_height(self):
        block_height = 2365

        with patch.object(self._key_value_storage, '_set_value'):
            self._key_value_storage.set_last_checked_coin_block_height(block_height)

            self._key_value_storage._set_value.assert_called_once_with(MongoKeyValueStorageImpl._COIN_BLOCK_HEIGHT_KEY,
                                                                       block_height)

    def test_get_last_checked_coin_block_height(self):
        block_height = 2365

        with patch.object(self._key_value_storage, '_get_value'):
            self._key_value_storage._get_value.return_value = block_height

            self.assertEqual(self._key_value_storage.get_last_checked_coin_block_height(), block_height)

            self._key_value_storage._get_value.assert_called_once_with(MongoKeyValueStorageImpl._COIN_BLOCK_HEIGHT_KEY)
