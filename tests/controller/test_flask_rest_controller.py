from logging import Logger
from typing import cast, Optional
from unittest import TestCase
from unittest.mock import MagicMock, patch

from waves_gateway.serializer import TransactionAttemptListSerializer, PublicConfigurationSerializer

from waves_gateway.controller import FlaskRestController, GatewayController
from waves_gateway.model import PublicConfiguration, AttemptListQuery


class FlaskRestControllerSpec(TestCase):
    def setUp(self):
        self._gateway_controller = MagicMock()
        self._flask = MagicMock()
        self._logger = MagicMock()
        self._attempt_list_serializer = MagicMock()
        self._base_currency_name = 'Turtle Network'
        self._custom_currency_name = 'Test Coin'
        self._public_configuration = MagicMock()
        self._public_configuration_serializer = MagicMock()

        self.flask_setup = FlaskRestController(
            flask=self._flask,
            gateway_controller=cast(GatewayController, self._gateway_controller),
            logger=cast(Logger, self._logger),
            public_configuration=cast(PublicConfiguration, self._public_configuration),
            attempt_list_serializer=cast(TransactionAttemptListSerializer, self._attempt_list_serializer),
            public_configuration_serializer=cast(PublicConfigurationSerializer, self._public_configuration_serializer))

    def test_create_address(self):
        coin_address = '028735'
        waves_address = '97368487'

        self._gateway_controller.create_address.return_value = coin_address

        res = self.flask_setup._create_address(waves_address)

        self._gateway_controller.create_address.assert_called_once_with(waves_address)
        self.assertEqual(res, coin_address)

    @patch('flask.abort', autospec=True)
    def test_get_attempt_list_by_id_not_found(self, abort_mock: MagicMock):
        self._gateway_controller.get_attempt_list_by_id.return_value = None
        attempt_list_id = '927653'

        self.flask_setup._get_attempt_list_by_id(attempt_list_id)

        self._gateway_controller.get_attempt_list_by_id.assert_called_once_with(attempt_list_id)
        self._attempt_list_serializer.attempt_list_as_dict.assert_not_called()
        abort_mock.assert_called_once_with(404)

    @patch('flask.abort', autospec=True)
    @patch('flask.jsonify', autospec=True)
    def test_get_attempt_list_by_id_with_result(self, jsonify_mock: MagicMock, abort_mock: MagicMock):
        attempt_list_result = MagicMock()
        attempt_list_id = '927653'
        attempt_list_as_dict = MagicMock()
        jsonify_result = MagicMock()

        self._gateway_controller.get_attempt_list_by_id.return_value = attempt_list_result
        self._attempt_list_serializer.attempt_list_as_dict.return_value = attempt_list_as_dict
        jsonify_mock.return_value = jsonify_result

        res = self.flask_setup._get_attempt_list_by_id(attempt_list_id)

        self.assertIs(res, jsonify_result)
        self._gateway_controller.get_attempt_list_by_id.assert_called_once_with(attempt_list_id)
        self._attempt_list_serializer.attempt_list_as_dict.assert_called_once_with(attempt_list_result)
        self.assertEqual(abort_mock.call_count, 0)
        jsonify_mock.assert_called_once_with(attempt_list_as_dict)

    @patch('flask.abort', autospec=True)
    @patch('flask.request', autospec=True)
    @patch('flask.jsonify', autospec=True)
    def test_get_attempt_list_with_anything(self, jsonify_mock: MagicMock, request: MagicMock, abort_mock: MagicMock):

        arg_anything = '79365487'
        expected_query = AttemptListQuery(anything=arg_anything)
        query_result = MagicMock()
        query_result_as_dict = MagicMock()
        jsonify_result = MagicMock

        def get_arg(arg: str) -> Optional[str]:
            if arg == 'anything':
                return arg_anything
            else:
                return None

        self._gateway_controller.query_attempt_lists.return_value = [query_result]
        request.args = MagicMock()
        request.args.get = MagicMock()
        request.args.get.side_effect = get_arg
        self._attempt_list_serializer.attempt_list_as_dict.return_value = query_result_as_dict
        jsonify_mock.return_value = jsonify_result

        res = self.flask_setup._get_attempt_list()

        self.assertEqual(res, jsonify_result)
        jsonify_mock.assert_called_once_with([query_result_as_dict])
        self._attempt_list_serializer.attempt_list_as_dict.assert_called_once_with(query_result)
        self._gateway_controller.query_attempt_lists.assert_called_once_with(expected_query)
        self.assertEqual(abort_mock.call_count, 0)
