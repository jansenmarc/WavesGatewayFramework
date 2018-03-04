import unittest
from typing import cast
from unittest.mock import MagicMock

from waves_gateway.model import KeyPair

from waves_gateway.serializer import KeyPairSerializer
from waves_gateway.storage import MongoWalletStorageImpl
from pymongo.collection import Collection


class MongoWalletStorageImplTest(unittest.TestCase):
    def setUp(self):
        self._key_pair_serializer = MagicMock()
        self._collection = MagicMock()

        self._wallet_storage = MongoWalletStorageImpl(
            serializer=cast(KeyPairSerializer, self._key_pair_serializer),
            collection=cast(Collection, self._collection))

    def test_save_address_secret(self):
        mock_key_pair = KeyPair(public="7296357", secret="172o7358")
        mock_serialized_key_pair = MagicMock()

        self._key_pair_serializer.as_dict.return_value = mock_serialized_key_pair

        self._wallet_storage.save_address_secret(mock_key_pair)

        self._collection.insert_one.assert_called_once_with(mock_serialized_key_pair)

    def test_get_secret_by_public_address_no_result(self):
        mock_public_address = "71893928"
        expected_query = dict()
        expected_query[KeyPair.DICT_PUBLIC_KEY] = mock_public_address

        self._collection.find_one.return_value = None

        res = self._wallet_storage.get_secret_by_public_address(mock_public_address)

        self._collection.find_one.assert_called_once_with(expected_query)
        self.assertIsNone(res)

    def test_get_secret_by_public_address_found_result(self):
        mock_public_address = "71893928"
        expected_query = dict()
        expected_query[KeyPair.DICT_PUBLIC_KEY] = mock_public_address
        mock_find_one_result = MagicMock()
        mock_from_dict_result = MagicMock()

        self._collection.find_one.return_value = mock_find_one_result
        self._key_pair_serializer.from_dict.return_value = mock_from_dict_result

        res = self._wallet_storage.get_secret_by_public_address(mock_public_address)

        self._collection.find_one.assert_called_once_with(expected_query)
        self.assertEqual(res, mock_from_dict_result)
        self._key_pair_serializer.from_dict.assert_called_once_with(mock_find_one_result)
