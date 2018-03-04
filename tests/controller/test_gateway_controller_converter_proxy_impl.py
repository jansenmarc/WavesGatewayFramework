import unittest
from typing import cast
from unittest.mock import MagicMock

from waves_gateway.model import AttemptListQuery, AttemptListTrigger

from waves_gateway.controller import GatewayControllerConverterProxyImpl, GatewayController
from waves_gateway.service import AttemptListConverterService


class GatewayControllerConverterProxyImplSpec(unittest.TestCase):
    def setUp(self):
        self._converter = MagicMock()
        self._gateway_controller = MagicMock()
        self._proxy = GatewayControllerConverterProxyImpl(
            attempt_list_converter_service=cast(AttemptListConverterService, self._converter),
            gateway_controller=cast(GatewayController, self._gateway_controller))

    def test_query_attempt_lists(self):
        mock_query_result = MagicMock()
        mock_converted_result = MagicMock()
        mock_query = AttemptListQuery(anything="9327468")

        self._gateway_controller.query_attempt_lists.return_value = [mock_query_result]
        self._converter.revert_attempt_list_conversion.return_value = mock_converted_result

        res = self._proxy.query_attempt_lists(mock_query)

        self._gateway_controller.query_attempt_lists.assert_called_once_with(mock_query)
        self._converter.revert_attempt_list_conversion.assert_called_once_with(mock_query_result)
        self.assertEqual(res, [mock_converted_result])

    def test_get_attempt_list_by_trigger(self):
        mock_trigger = AttemptListTrigger(tx="2937468", currency="coin", receiver=0)
        mock_attempt_list = MagicMock()
        mock_converter_result = MagicMock()

        self._gateway_controller.get_attempt_list_by_trigger.return_value = mock_attempt_list
        self._converter.revert_attempt_list_conversion.return_value = mock_converter_result

        res = self._proxy.get_attempt_list_by_trigger(mock_trigger)

        self._converter.revert_attempt_list_conversion.assert_called_once_with(mock_attempt_list)
        self._gateway_controller.get_attempt_list_by_trigger.assert_called_once_with(mock_trigger)
        self.assertEqual(res, mock_converter_result)

    def test_create_address(self):
        mock_result = MagicMock()
        self._gateway_controller.create_address.return_value = mock_result
        mock_waves_address = "7923468"

        res = self._proxy.create_address(mock_waves_address)

        self.assertEqual(res, mock_result)
        self._gateway_controller.create_address.assert_called_once_with(mock_waves_address)

    def test_get_attempt_list_by_id_not_found(self):
        mock_id = "379468"

        self._gateway_controller.get_attempt_list_by_id.return_value = None

        res = self._proxy.get_attempt_list_by_id(mock_id)

        self.assertIsNone(res)

    def test_get_attempt_list_by_id_found_result(self):
        mock_id = "379468"
        mock_result = MagicMock()
        mock_converted_result = MagicMock()

        self._gateway_controller.get_attempt_list_by_id.return_value = mock_result
        self._converter.revert_attempt_list_conversion.return_value = mock_converted_result

        res = self._proxy.get_attempt_list_by_id(mock_id)

        self.assertEqual(res, mock_converted_result)
        self._gateway_controller.get_attempt_list_by_id.assert_called_once_with(mock_id)
        self._converter.revert_attempt_list_conversion.assert_called_once_with(mock_result)

    def test_check_coin_transaction(self):
        mock_tx = "7236895"
        self._proxy.check_coin_transaction(mock_tx)
        self._gateway_controller.check_coin_transaction.assert_called_once_with(mock_tx)

    def test_check_waves_transaction(self):
        mock_tx = "7236895"
        self._proxy.check_waves_transaction(mock_tx)
        self._gateway_controller.check_waves_transaction.assert_called_once_with(mock_tx)
