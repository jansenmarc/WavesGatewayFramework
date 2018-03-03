import unittest
from unittest.mock import patch, MagicMock
from typing import Any, cast
from waves_gateway.common import DuplicateMappingError
from waves_gateway.model import MappingEntry
from waves_gateway.storage import MapStorage


class MapStorageSpec(unittest.TestCase):
    @patch.multiple(MapStorage, __abstractmethods__=set())  # type: ignore
    def setUp(self):
        self._map_storage = cast(Any, MapStorage())

    def test_coin_address_exists_success(self):
        address = '82365'

        with patch.multiple(self._map_storage, get_waves_address_by_coin_address=MagicMock()):
            self._map_storage.get_waves_address_by_coin_address.return_value = MagicMock()
            self.assertTrue(self._map_storage.coin_address_exists(address))
            self._map_storage.get_waves_address_by_coin_address.assert_called_once_with(address)

    def test_coin_address_exists_failure(self):
        address = '82365'

        with patch.multiple(self._map_storage, get_waves_address_by_coin_address=MagicMock()):
            self._map_storage.get_waves_address_by_coin_address.return_value = None
            self.assertFalse(self._map_storage.coin_address_exists(address))
            self._map_storage.get_waves_address_by_coin_address.assert_called_once_with(address)

    def test_waves_address_exists_success(self):
        address = '82365'

        with patch.multiple(self._map_storage, get_coin_address_by_waves_address=MagicMock()):
            self._map_storage.get_coin_address_by_waves_address.return_value = MagicMock()
            self.assertTrue(self._map_storage.waves_address_exists(address))
            self._map_storage.get_coin_address_by_waves_address.assert_called_once_with(address)

    def test_waves_address_exists_failure(self):
        address = '82365'

        with patch.multiple(self._map_storage, get_coin_address_by_waves_address=MagicMock()):
            self._map_storage.get_coin_address_by_waves_address.return_value = None
            self.assertFalse(self._map_storage.waves_address_exists(address))
            self._map_storage.get_coin_address_by_waves_address.assert_called_once_with(address)

    def test_safely_save_mapping_waves_address_exists(self):
        mapping = MappingEntry(coin_address='34435', waves_address='3432')

        with patch.multiple(
                self._map_storage,
                waves_address_exists=MagicMock(),
                coin_address_exists=MagicMock(),
                save_mapping=MagicMock()):
            self._map_storage.waves_address_exists.return_value = True
            self._map_storage.coin_address_exists.return_value = False

            with self.assertRaises(DuplicateMappingError):
                self._map_storage.safely_save_mapping(mapping)

            self._map_storage.waves_address_exists.assert_called_once_with(mapping.waves_address)
            self._map_storage.coin_address_exists.assert_not_called()
            self._map_storage.save_mapping.assert_not_called()

    def test_safely_save_mapping_coin_address_exists(self):
        mapping = MappingEntry(coin_address='34435', waves_address='3432')

        with patch.multiple(
                self._map_storage,
                waves_address_exists=MagicMock(),
                coin_address_exists=MagicMock(),
                save_mapping=MagicMock()):
            self._map_storage.waves_address_exists.return_value = False
            self._map_storage.coin_address_exists.return_value = True

            with self.assertRaises(DuplicateMappingError):
                self._map_storage.safely_save_mapping(mapping)

            self._map_storage.waves_address_exists.assert_called_once_with(mapping.waves_address)
            self._map_storage.coin_address_exists.assert_called_once_with(mapping.coin_address)
            self._map_storage.save_mapping.assert_not_called()

    def test_safely_save_mapping_success(self):
        mapping = MappingEntry(coin_address='34435', waves_address='3432')

        with patch.multiple(
                self._map_storage,
                waves_address_exists=MagicMock(),
                coin_address_exists=MagicMock(),
                save_mapping=MagicMock()):
            self._map_storage.waves_address_exists.return_value = False
            self._map_storage.coin_address_exists.return_value = False

            self._map_storage.safely_save_mapping(mapping)

            self._map_storage.waves_address_exists.assert_called_once_with(mapping.waves_address)
            self._map_storage.coin_address_exists.assert_called_once_with(mapping.coin_address)
            self._map_storage.save_mapping.assert_called_once_with(mapping)
