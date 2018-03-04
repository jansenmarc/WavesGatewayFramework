import unittest
from typing import cast
from unittest.mock import MagicMock

import pywaves  # type: ignore

from waves_gateway.model import KeyPair
from waves_gateway.storage import WalletStorage
from waves_gateway.service import SecretService


class SecretServiceSpec(unittest.TestCase):
    def setUp(self):
        self._wallet_storage = MagicMock()
        self._coin_gateway_address_secret = KeyPair('937846', '79632748')
        self._gateway_pywaves_address = MagicMock()
        self._gateway_pywaves_address.address = '9786296758'
        self._gateway_pywaves_address.privateKey = '92758'

        self._secret_service = SecretService(
            wallet_storage=cast(WalletStorage, self._wallet_storage),
            gateway_coin_address_secret=cast(KeyPair, self._coin_gateway_address_secret),
            gateway_pywaves_address=cast(pywaves.Address, self._gateway_pywaves_address))

    def test_get_secret_by_address_waves(self):
        res = self._secret_service.get_secret_by_address('waves', self._gateway_pywaves_address.address)
        self.assertEqual(res, self._gateway_pywaves_address.privateKey)

    def test_get_secret_by_address_gateway_address(self):
        res = self._secret_service.get_secret_by_address('coin', self._coin_gateway_address_secret.public)
        self.assertEqual(res, self._coin_gateway_address_secret.secret)

    def test_get_secret_by_address_other(self):
        address = '802389724'
        secret = '8023984'
        pair = KeyPair(address, secret)

        self._wallet_storage.get_secret_by_public_address.return_value = pair

        res = self._secret_service.get_secret_by_address('coin', address)

        self.assertEqual(res, secret)
        self._wallet_storage.get_secret_by_public_address.assert_called_once_with(address)

    def test_get_secret_by_address_other_not_found(self):
        address = '8023835424'

        self._wallet_storage.get_secret_by_public_address.return_value = None

        res = self._secret_service.get_secret_by_address('coin', address)

        self.assertEqual(res, None)
