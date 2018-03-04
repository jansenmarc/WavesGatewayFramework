import unittest
from typing import cast
from unittest.mock import MagicMock
from pymongo.collection import Collection  # type: ignore
from waves_gateway.model import MappingEntry
from waves_gateway.serializer import MappingEntrySerializer
from waves_gateway.storage import MongoMapStorageImpl


class MongoMapStorageImplTest(unittest.TestCase):
    def setUp(self):
        self._collection = MagicMock()
        self._serializer = MagicMock()

        self._map_storage = MongoMapStorageImpl(
            collection=cast(Collection, self._collection), serializer=cast(MappingEntrySerializer, self._serializer))

    def test_save_mapping(self):
        mock_mapping = MappingEntry(coin_address="23535", waves_address="3425246")
        mock_serialized_mapping = MagicMock()
        self._serializer.as_dict.return_value = mock_serialized_mapping

        self._map_storage.save_mapping(mock_mapping)

        self._collection.insert_one.assert_called_once_with(mock_serialized_mapping)

    def test_get_waves_address_by_coin_address_not_found(self):
        mock_coin_address = "2353523"
        expected_query = dict()
        expected_query[MappingEntry.DICT_COIN_KEY] = mock_coin_address

        self._collection.find_one.return_value = None

        res = self._map_storage.get_waves_address_by_coin_address(mock_coin_address)

        self.assertIsNone(res)
        self._collection.find_one.assert_called_once_with(expected_query)

    def test_get_waves_address_by_coin_address_found_result(self):
        mock_coin_address = "2353523"
        mock_waves_address = "9287346"
        expected_query = dict()
        expected_query[MappingEntry.DICT_COIN_KEY] = mock_coin_address
        mock_find_one_result = dict()
        mock_find_one_result[MappingEntry.DICT_WAVES_KEY] = mock_waves_address

        self._collection.find_one.return_value = mock_find_one_result

        res = self._map_storage.get_waves_address_by_coin_address(mock_coin_address)

        self.assertEqual(res, mock_waves_address)
        self._collection.find_one.assert_called_once_with(expected_query)

    def test_get_coin_address_by_waves_address_not_found(self):
        mock_waves_address = "2353523"
        expected_query = dict()
        expected_query[MappingEntry.DICT_WAVES_KEY] = mock_waves_address

        self._collection.find_one.return_value = None

        res = self._map_storage.get_coin_address_by_waves_address(mock_waves_address)

        self.assertIsNone(res)
        self._collection.find_one.assert_called_once_with(expected_query)

    def test_get_coin_address_by_waves_address_found_result(self):
        mock_coin_address = "2353523"
        mock_waves_address = "9287346"
        expected_query = dict()
        expected_query[MappingEntry.DICT_WAVES_KEY] = mock_waves_address
        mock_find_one_result = dict()
        mock_find_one_result[MappingEntry.DICT_WAVES_KEY] = mock_waves_address
        mock_find_one_result[MappingEntry.DICT_COIN_KEY] = mock_coin_address

        self._collection.find_one.return_value = mock_find_one_result

        res = self._map_storage.get_coin_address_by_waves_address(mock_waves_address)

        self.assertEqual(res, mock_coin_address)
        self._collection.find_one.assert_called_once_with(expected_query)
