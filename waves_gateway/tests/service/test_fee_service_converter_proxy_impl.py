import unittest
from typing import cast
from unittest.mock import MagicMock

from waves_gateway.service import FeeServiceConverterProxyImpl, IntegerConverterService, FeeService


class FeeServiceConverterProxyImplSpec(unittest.TestCase):
    def setUp(self):
        self._fee_service = MagicMock()
        self.coin_integer_converter = MagicMock()

        self._fee_service_converter_proxy = FeeServiceConverterProxyImpl(
            fee_service=cast(FeeService, self._fee_service),
            coin_integer_converter_service=cast(IntegerConverterService, self.coin_integer_converter))

    def test_get_gateway_fee(self):
        mock_gateway_fee = MagicMock()
        mock_convert_to_int_result = MagicMock()
        self._fee_service.get_gateway_fee.return_value = mock_gateway_fee
        self.coin_integer_converter.safely_convert_to_int.return_value = mock_convert_to_int_result

        res = self._fee_service_converter_proxy.get_gateway_fee()

        self.assertEqual(res, mock_convert_to_int_result)
        self.coin_integer_converter.safely_convert_to_int.assert_called_once_with(mock_gateway_fee)

    def test_get_coin_fee(self):
        mock_coin_fee = MagicMock()
        mock_convert_to_int_result = MagicMock()
        self._fee_service.get_coin_fee.return_value = mock_coin_fee
        self.coin_integer_converter.safely_convert_to_int.return_value = mock_convert_to_int_result

        res = self._fee_service_converter_proxy.get_coin_fee()

        self.assertEqual(res, mock_convert_to_int_result)
        self.coin_integer_converter.safely_convert_to_int.assert_called_once_with(mock_coin_fee)

    def test_get_waves_fee(self):
        mock_waves_fee = MagicMock()
        self._fee_service.get_waves_fee.return_value = mock_waves_fee

        res = self._fee_service_converter_proxy.get_waves_fee()

        self.assertEqual(res, mock_waves_fee)
