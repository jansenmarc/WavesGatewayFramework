import unittest
from unittest.mock import patch, MagicMock

from waves_gateway import TransactionAttempt, TransactionAttemptReceiver, Transaction, TransactionReceiver
from waves_gateway.service import AssetTransactionServiceImpl


class AssetTransactionServiceImplTest(unittest.TestCase):
    def setUp(self):
        self._waves_asset_id = "29768357"
        self._gateway_pywaves_address = MagicMock()
        self._gateway_pywaves_address.address = "9234568"

    @patch('pywaves.Asset', autospec=True)
    @patch('pywaves.Address', autospec=True)
    def test_send_coin(self, mock_address_class: MagicMock, mock_asset_class: MagicMock):
        mock_transaction_receiver = TransactionAttemptReceiver(address="89237456", amount=213)

        mock_transaction_attempt = TransactionAttempt(
            currency="waves", fee=324, receivers=[mock_transaction_receiver], sender="9234568")

        mock_asset_instance = MagicMock()
        mock_receiver_address_instance = MagicMock()
        mock_secret = "8293645"

        mock_asset_class.return_value = mock_asset_instance
        mock_address_class.return_value = mock_receiver_address_instance

        expected_transaction = Transaction(
            tx="728963457",
            receivers=[
                TransactionReceiver(address=mock_transaction_receiver.address, amount=mock_transaction_receiver.amount)
            ])

        mock_send_asset_result = {'id': expected_transaction.tx, 'recipient': mock_transaction_receiver.address}

        self._gateway_pywaves_address.sendAsset.return_value = mock_send_asset_result

        transaction_service = AssetTransactionServiceImpl(self._waves_asset_id, self._gateway_pywaves_address)

        transaction = transaction_service.send_coin(mock_transaction_attempt, mock_secret)

        self._gateway_pywaves_address.sendAsset.assert_called_once_with(
            recipient=mock_receiver_address_instance,
            asset=mock_asset_instance,
            amount=mock_transaction_receiver.amount,
            txFee=mock_transaction_attempt.fee)

        self.assertEqual(transaction, expected_transaction)
        mock_address_class.assert_called_once_with(mock_transaction_attempt.receivers[0].address)
