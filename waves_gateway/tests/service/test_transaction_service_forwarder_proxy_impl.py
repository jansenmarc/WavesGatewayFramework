import unittest
from typing import cast
from unittest.mock import MagicMock

from waves_gateway import TransactionService, TransactionAttempt
from waves_gateway.service import TransactionServiceForwarderProxyImpl


class TransactionServiceForwarderProxyImplSpec(unittest.TestCase):
    def setUp(self):
        self._coin_transaction_service = MagicMock()
        self._asset_transaction_service = MagicMock()
        self._transaction_service_forwarder_proxy = TransactionServiceForwarderProxyImpl(
            coin_transaction_service=cast(TransactionService, self._coin_transaction_service),
            asset_transaction_service=cast(TransactionService, self._asset_transaction_service))

    def test_send_coin_currency_coin(self):
        attempt = TransactionAttempt(sender="hgksjgj", receivers=[], fee=346, currency="coin")
        secret = "293876478"
        mock_send_coin_result = MagicMock()

        self._coin_transaction_service.send_coin.return_value = mock_send_coin_result

        transaction = self._transaction_service_forwarder_proxy.send_coin(attempt, secret)

        self.assertEqual(transaction, mock_send_coin_result)
        self._asset_transaction_service.send_coin.assert_not_called()
        self._coin_transaction_service.send_coin.assert_called_once_with(attempt, secret)

    def test_send_coin_currency_waves(self):
        attempt = TransactionAttempt(sender="hgksjgj", receivers=[], fee=346, currency="waves")
        secret = "293876478"
        mock_send_coin_result = MagicMock()

        self._asset_transaction_service.send_coin.return_value = mock_send_coin_result

        transaction = self._transaction_service_forwarder_proxy.send_coin(attempt, secret)

        self.assertEqual(transaction, mock_send_coin_result)
        self._coin_transaction_service.send_coin.assert_not_called()
        self._asset_transaction_service.send_coin.assert_called_once_with(attempt, secret)
