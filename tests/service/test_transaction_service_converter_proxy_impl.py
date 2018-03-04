import unittest
from typing import cast
from unittest.mock import MagicMock

from waves_gateway import IntegerConverterService, TransactionService, TransactionAttempt
from waves_gateway.service import TransactionServiceConverterProxyImpl, AttemptListConverterService


class AssetTransactionServiceConverterProxyImplTest(unittest.TestCase):
    def setUp(self):
        self._integer_converter_service = MagicMock()
        self._transaction_service = MagicMock()
        self._attempt_list_converter_service = MagicMock()

        self._proxy = TransactionServiceConverterProxyImpl(
            integer_converter_service=cast(IntegerConverterService, self._integer_converter_service),
            transaction_service=cast(TransactionService, self._transaction_service),
            attempt_list_converter_service=cast(AttemptListConverterService, self._attempt_list_converter_service))

    def test_send_coin(self):
        mock_revert_attempt_conversion_result = MagicMock()
        mock_convert_to_int_result = MagicMock()
        mock_attempt = cast(TransactionAttempt, MagicMock)
        mock_secret = "826357"

        self._attempt_list_converter_service.revert_attempt_conversion.return_value = mock_revert_attempt_conversion_result
        self._integer_converter_service.convert_transaction_to_int.return_value = mock_convert_to_int_result

        res = self._proxy.send_coin(mock_attempt, mock_secret)

        self._transaction_service.send_coin.assert_called_once_with(mock_revert_attempt_conversion_result, mock_secret)
        self.assertEqual(res, mock_convert_to_int_result)
