import unittest
from typing import cast
from unittest.mock import MagicMock

from waves_gateway import IntegerConverterService, ChainQueryService
from waves_gateway.service import ChainQueryServiceConverterProxyImpl


class ChainQueryServiceConverterProxyImplTest(unittest.TestCase):
    def setUp(self):
        self._integer_converter_service = MagicMock()
        self._chain_query_service = MagicMock()

        self._proxy = ChainQueryServiceConverterProxyImpl(
            integer_converter_service=cast(IntegerConverterService, self._integer_converter_service),
            chain_query_service=cast(ChainQueryService, self._chain_query_service))

    def test_get_coin_receiver_address_from_transaction(self):
        mock_result = MagicMock()
        self._chain_query_service.get_coin_receiver_address_from_transaction.return_value = mock_result

        res = self._proxy.get_coin_receiver_address_from_transaction("978153")

        self.assertEqual(res, mock_result)

    def test_get_height_of_highest_block(self):
        mock_result = MagicMock()
        self._chain_query_service.get_height_of_highest_block.return_value = mock_result
        res = self._proxy.get_height_of_highest_block()
        self.assertEqual(res, mock_result)

    def test_get_transactions_of_block_at_height(self):
        mock_first_transaction = MagicMock()
        mock_second_transaction = MagicMock()
        mock_first_converted_transaction = MagicMock()
        mock_second_converted_transaction = MagicMock()
        mock_height = 234

        self._chain_query_service.get_transactions_of_block_at_height.return_value = [
            mock_first_transaction, mock_second_transaction
        ]

        def mock_convert_transaction_to_int(transaction: MagicMock):
            if transaction is mock_first_transaction:
                return mock_first_converted_transaction
            elif transaction is mock_second_transaction:
                return mock_second_converted_transaction
            else:
                raise Exception('unknown transaction')

        self._integer_converter_service.convert_transaction_to_int.side_effect = mock_convert_transaction_to_int

        res = self._proxy.get_transactions_of_block_at_height(mock_height)

        self.assertEqual(res, [mock_first_converted_transaction, mock_second_converted_transaction])
        self._integer_converter_service.convert_transaction_to_int.assert_any_call(mock_first_transaction)
        self._integer_converter_service.convert_transaction_to_int.assert_any_call(mock_second_transaction)
