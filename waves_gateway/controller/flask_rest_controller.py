"""
FlaskRestController
"""

from logging import Logger
from typing import Any, List, Callable, Optional

from waves_gateway.common import map_array, WavesAddressInvalidError, InvalidTransactionIdentifier, Injectable, API_KEY

import flask as flask_module  # type: ignore

from waves_gateway.model.public_configuration import PublicConfiguration
from waves_gateway.serializer import TransactionAttemptListSerializer
from waves_gateway.serializer.public_configuration_serializer import PublicConfigurationSerializer

from .gateway_controller import GatewayController, AttemptListQuery
from .gateway_controller_converter_proxy_impl import GatewayControllerConverterProxyImpl


@Injectable(deps=[
    flask_module.Flask, GatewayControllerConverterProxyImpl, Logger, TransactionAttemptListSerializer,
    PublicConfiguration, PublicConfigurationSerializer, API_KEY
])
class FlaskRestController(object):
    """
    Optional Flask based rest interface for the Gateway.
    Forwards ReST requests to the general GatewayController.
    """

    def _add_url_rule(self, rule: str, endpoint: str, view_func: Callable, methods: List[str] = None):
        self._logger.info('Registered %s %s', str(methods), rule)

        def catch(*args, **kwargs):
            """
            Forwards the request to the concrete handler function.
            """
            try:
                return view_func(*args, **kwargs)
            except BaseException as ex:
                if hasattr(ex, 'code'):
                    raise ex
                else:
                    self._logger.error(ex, exc_info=True)
                    flask_module.abort(500)

        self._flask.add_url_rule(rule, endpoint, catch, methods=methods)

    def __init__(self, flask: Any, gateway_controller: GatewayController, logger: Logger,
                 attempt_list_serializer: TransactionAttemptListSerializer, public_configuration: PublicConfiguration,
                 public_configuration_serializer: PublicConfigurationSerializer, api_key: str) -> None:
        self._flask = flask
        self._gateway_controller = gateway_controller
        self._logger = logger.getChild(self.__class__.__name__)
        self._serializer = attempt_list_serializer
        self._public_configuration = public_configuration
        self._public_configuration_serializer = public_configuration_serializer
        self._key = api_key

        self._add_url_rule('/api/v1', 'heartbeat', lambda: "", methods=['GET'])

        self._add_url_rule(
            '/api/v1/coin-address/<waves_address>',
            'create_address',
            lambda waves_address: self._create_address(waves_address),
            methods=['GET'])

        self._add_url_rule(
            '/api/v1/attempt-list', 'get_attempt_list', lambda: self._get_attempt_list(), methods=['GET'])

        self._add_url_rule(
            '/api/v1/average-attempt-list-tries',
            'get_average_attempt_list_tries',
            lambda: self._get_average_attempt_list_tries(),
            methods=['GET'])

        self._add_url_rule(
            '/api/v1/block-heights', 'get_coin_blockheight', lambda: self._get_block_heights(), methods=['GET'])

        self._add_url_rule(
            '/api/v1/failed-transaction',
            'get_failed_transaction',
            lambda: self._get_failed_transactions(),
            methods=['GET'])

        self._add_url_rule(
            '/api/v1/log-messages', 'get_log_messages', lambda: self._get_log_messages(), methods=['GET'])

        self._add_url_rule(
            '/api/v1/trigger-attemptlist-retry',
            'trigger_attemptlist_retry',
            lambda: self._trigger_attemptlist_retry(),
            methods=['GET'])

        self._add_url_rule(
            '/api/v1/attempt-list/<attempt_list_id>',
            'get_attempt_list_by_id',
            lambda attempt_list_id: self._get_attempt_list_by_id(attempt_list_id),
            methods=['GET'])

        self._add_url_rule('/', 'redirect', lambda: flask_module.redirect('static/'), methods=['GET'])

        self._add_url_rule('/static/', 'index', lambda: flask_module.redirect('static/index.html'), methods=['GET'])

        self._add_url_rule(
            '/api/v1/public-config',
            'get_public_config',
            lambda: flask_module.jsonify(self._public_configuration_serializer.as_dict(self._public_configuration)),
            methods=['GET'])

        self._add_url_rule(
            '/api/v1/check/waves/<tx>', 'check_waves_tx', lambda tx: self._check_waves_transaction(tx), methods=['GET'])

        self._add_url_rule(
            '/api/v1/check/coin/<tx>', 'check_coin_tx', lambda tx: self._check_coin_transaction(tx), methods=['GET'])

    def _create_address(self, waves_address: str) -> str:
        """
        Forwards an create address request to the GatewayController.
        """
        try:
            coin_address = self._gateway_controller.create_address(waves_address)
        except WavesAddressInvalidError:
            return flask_module.abort(400)

        return coin_address

    def _get_failed_transactions(self):
        key = flask_module.request.headers['api-key']
        if key is not None and key == self._key:
            failed_transactions = self._gateway_controller.get_failed_transactions()
            return flask_module.jsonify(failed_transactions)
        else:
            flask_module.abort(403)

    def _get_log_messages(self):
        key = flask_module.request.headers['api-key']
        if key is not None and key == self._key:
            log_messages = self._gateway_controller.get_log_messages()
            return flask_module.jsonify(log_messages)
        else:
            flask_module.abort(403)

    def _get_average_attempt_list_tries(self):
        key = flask_module.request.headers['api-key']
        if key is not None and key == self._key:
            data = self._gateway_controller.get_average_attempt_list_tries()
            return flask_module.jsonify(data)
        else:
            flask_module.abort(403)

    def _get_attempt_list_by_id(self, attempt_list_id: str) -> Optional[str]:
        attempt_list = self._gateway_controller.get_attempt_list_by_id(attempt_list_id)

        if attempt_list is None:
            return flask_module.abort(404)

        serialized = self._serializer.attempt_list_as_dict(attempt_list)

        return flask_module.jsonify(serialized)

    def _get_attempt_list(self) -> str:
        trigger_tx = flask_module.request.args.get('trigger_tx')  # type: Optional[str]
        trigger_currency = flask_module.request.args.get('trigger_currency')  # type: Optional[str]
        trigger_receiver = flask_module.request.args.get('trigger_receiver')  # type: Optional[str]
        anything = flask_module.request.args.get('anything')  # type: Optional[str]
        attempt = flask_module.request.args.get('attempt')  # type: Optional[int]
        tries = flask_module.request.args.get('tries')  # type: Optional[int]

        trigger_receiver_as_int = None  # type: Optional[int]

        if trigger_receiver is not None:
            trigger_receiver_as_int = int(trigger_receiver)

        if (trigger_tx is None) and (anything is None) and (attempt is None) and (tries is None):
            return flask_module.abort(400)

        query = AttemptListQuery(
            trigger_currency=trigger_currency,
            trigger_tx=trigger_tx,
            trigger_receiver=trigger_receiver_as_int,
            anything=anything,
            attempt=attempt,
            tries=tries)

        attempt_lists = self._gateway_controller.query_attempt_lists(query)

        serialized_lists = map_array(lambda x: self._serializer.attempt_list_as_dict(x), attempt_lists)

        return flask_module.jsonify(serialized_lists)

    def _check_coin_transaction(self, tx: str):
        key = flask_module.request.headers['api-key']
        if key is not None and key == self._key:
            try:
                self._gateway_controller.check_coin_transaction(tx)
            except InvalidTransactionIdentifier:
                flask_module.abort(400)
            except NotImplementedError:
                flask_module.abort(501)

            return ''
        else:
            flask_module.abort(403)

    def _get_block_heights(self):
        key = flask_module.request.headers['api-key']
        if key is not None and key == self._key:
            heights = self._gateway_controller.get_block_heights()
            return flask_module.jsonify(heights)
        else:
            flask_module.abort(403)

    def _check_waves_transaction(self, tx: str):
        key = flask_module.request.headers['api-key']
        if key is not None and key == self._key:
            try:
                self._gateway_controller.check_waves_transaction(tx)
            except InvalidTransactionIdentifier:
                flask_module.abort(400)

            return ''
        else:
            flask_module.abort(403)

    def _trigger_attemptlist_retry(self):
        key = flask_module.request.headers['api-key']
        if key is not None and key == self._key:
            attempt_list_id = flask_module.request.args.get('attempt_list_id')  # type: Optional[str]
            retry_was_successful = self._gateway_controller.trigger_attemptlist_retry(attempt_list_id)
            if retry_was_successful:
                return
            else:
                flask_module.abort(400)
        else:
            flask_module.abort(403)
