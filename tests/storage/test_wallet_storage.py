"""
WalletStorageSpec
"""

import unittest
from unittest.mock import patch, MagicMock
from typing import Any, cast

from waves_gateway.model import KeyPair
from waves_gateway.common import DuplicateSecretError
from waves_gateway.storage import WalletStorage


class WalletStorageSpec(unittest.TestCase):
    @patch.multiple(WalletStorage, __abstractmethods__=set())  # type: ignore
    def setUp(self):
        self._wallet_storage = cast(Any, WalletStorage())

    def test_safely_save_address_secret_raises(self):
        key_pair = KeyPair(public='pub', secret='sec')

        with patch.multiple(self._wallet_storage, public_address_exists=MagicMock(), save_address_secret=MagicMock()):
            self._wallet_storage.public_address_exists.return_value = True

            with self.assertRaises(DuplicateSecretError):
                self._wallet_storage.safely_save_address_secret(key_pair)

            self._wallet_storage.public_address_exists.assert_called_once_with(key_pair.public)
            self._wallet_storage.save_address_secret.assert_not_called()

    def test_safely_save_address_secret_success(self):
        key_pair = KeyPair(public='pub', secret='sec')

        with patch.multiple(self._wallet_storage, public_address_exists=MagicMock(), save_address_secret=MagicMock()):
            self._wallet_storage.public_address_exists.return_value = False

            self._wallet_storage.safely_save_address_secret(key_pair)

            self._wallet_storage.public_address_exists.assert_called_once_with(key_pair.public)
            self._wallet_storage.save_address_secret.assert_called_once_with(key_pair)

    def test_public_address_exists_success(self):
        address = '82365'

        with patch.multiple(self._wallet_storage, get_secret_by_public_address=MagicMock()):
            self._wallet_storage.get_secret_by_public_address.return_value = MagicMock()
            self.assertTrue(self._wallet_storage.public_address_exists(address))
            self._wallet_storage.get_secret_by_public_address.assert_called_once_with(address)

    def test_public_address_exists_failure(self):
        address = '82365'

        with patch.multiple(self._wallet_storage, get_secret_by_public_address=MagicMock()):
            self._wallet_storage.get_secret_by_public_address.return_value = None
            self.assertFalse(self._wallet_storage.public_address_exists(address))
            self._wallet_storage.get_secret_by_public_address.assert_called_once_with(address)
