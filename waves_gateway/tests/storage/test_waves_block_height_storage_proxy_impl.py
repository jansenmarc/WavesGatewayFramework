"""
WavesBlockHeightStorageProxyImplSpec
"""

from typing import cast
from unittest import TestCase
from unittest.mock import MagicMock

from waves_gateway.storage.key_value_storage import KeyValueStorage
from waves_gateway.storage.waves_block_height_storage_proxy_impl import WavesBlockHeightStorageProxyImpl


class WavesBlockHeightStorageProxyImplSpec(TestCase):
    def setUp(self):
        self._key_value_storage = MagicMock()
        self._block_height_storage_proxy = WavesBlockHeightStorageProxyImpl(
            key_value_storage=cast(KeyValueStorage, self._key_value_storage))

    def test_set_last_checked_block_height(self):
        block_height = 235
        self._block_height_storage_proxy.set_last_checked_block_height(block_height)
        self._key_value_storage.set_last_checked_waves_block_height.assert_called_once_with(block_height)
        self._key_value_storage.set_last_checked_coin_block_height.assert_not_called()

    def test_get_last_checked_block_height(self):
        block_height = 237856
        self._key_value_storage.get_last_checked_waves_block_height.return_value = block_height
        self.assertEqual(self._block_height_storage_proxy.get_last_checked_block_height(), block_height)
        self._key_value_storage.get_last_checked_waves_block_height.assert_called_once_with()
        self._key_value_storage.get_last_checked_coin_block_height.assert_not_called()
