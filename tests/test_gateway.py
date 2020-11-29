from unittest import TestCase
from unittest.mock import patch, MagicMock, ANY
from pymongo.database import Database as MongoDatabase  # type: ignore

import logging
import waves_gateway

from waves_gateway.factory import CoinAddressFactory

from waves_gateway.model import PollingDelayConfig
from waves_gateway.common import Injector, InjectorError, LOGGING_HANDLER_LIST, POLLING_DELAY_SECONDS, \
    BASE_CURRENCY_NAME, CUSTOM_CURRENCY_NAME, WALLET_STORAGE_COLLECTION_NAME, MAP_STORAGE_COLLECTION_NAME, \
    KEY_VALUE_STORAGE_COLLECTION_NAME, TRANSACTION_ATTEMPT_LIST_STORAGE_COLLECTION_NAME, GATEWAY_COIN_ADDRESS_SECRET, \
    KeyPair, GATEWAY_COIN_ADDRESS, WAVES_NODE, WAVES_ASSET_ID, WAVES_CHAIN, ONLY_ONE_TRANSACTION_RECEIVER, \
    COIN_TRANSACTION_WEB_LINK, WAVES_TRANSACTION_WEB_LINK, WAVES_ADDRESS_WEB_LINK, ATTEMPT_LIST_MAX_COMPLETION_TRIES, \
    GATEWAY_WAVES_ADDRESS_SECRET, GATEWAY_WAVES_ADDRESS
from waves_gateway.gateway import Gateway, flask_factory, logger_factory, \
    logging_handlers_factory, polling_delay_config_factory, collection_factory, coin_transaction_polling_service_factory, waves_transaction_polling_service_factory, public_configuration_factory, Gateway
from waves_gateway.service import GatewayApplicationService, GatewayLoggingConfigurationService, \
    COIN_CHAIN_QUERY_SERVICE, COIN_ADDRESS_VALIDATION_SERVICE
from waves_gateway.controller import FlaskRestController


class FactoryTest(TestCase):
    @patch('flask.Flask', autospec=True)
    def test_flask_factory(self, mock_flask: MagicMock):
        mock_flask_instance = MagicMock()
        mock_flask.return_value = mock_flask_instance
        flask_name = 'ltc-gateway'
        res = flask_factory(flask_name)
        mock_flask.assert_called_once_with(flask_name, static_folder=ANY)
        self.assertIs(res, mock_flask_instance)

    def test_logger_factory(self):
        mock_flask_logger = MagicMock()
        mock_flask = MagicMock()
        mock_flask.logger = mock_flask_logger
        mock_logging_handler = MagicMock()
        logging_handlers = [mock_logging_handler]
        mock_managed_logger = MagicMock()
        managed_loggers = [mock_managed_logger]

        res = logger_factory(mock_flask, logging_handlers, managed_loggers)

        mock_flask_logger.setLevel.assert_called_once_with(logging.DEBUG)
        mock_managed_logger.addHandler.assert_called_once_with(mock_logging_handler)
        mock_flask_logger.addHandler.assert_called_once_with(mock_logging_handler)
        self.assertIs(res, mock_flask_logger)

    def test_logging_handlers_factory(self):
        res = logging_handlers_factory()

        self.assertIsInstance(res, list)
        self.assertEqual(len(res), 1)
        self.assertIsInstance(res[0], logging.StreamHandler)

    @patch('waves_gateway.model.PollingDelayConfig', autospec=True)
    def test_polling_delay_config_factory_with_polling_delay_s(self, mock_polling_delay_config: MagicMock):
        mock_polling_delay_config_instance = MagicMock()
        mock_polling_delay_config.from_single_polling_delay.return_value = mock_polling_delay_config_instance
        polling_delay_s = 2
        res = polling_delay_config_factory(polling_delay_s)
        self.assertIs(res, mock_polling_delay_config_instance)
        mock_polling_delay_config.from_single_polling_delay.assert_called_once_with(polling_delay_s)

    def test_collection_factory(self):
        collection_name = "test_storage"
        database = MagicMock()
        collection = MagicMock()
        database.get_collection.return_value = collection

        res = collection_factory(collection_name, database)

        self.assertIs(res, collection)
        database.get_collection.assert_called_once_with(collection_name)

    @patch('waves_gateway.service.TransactionPollingService', autospec=True)
    def test_coin_transaction_polling_service_factory(self, mock_transaction_polling_service: MagicMock):
        chain_query_service = MagicMock()
        logger = MagicMock()
        block_height_storage = MagicMock()
        transaction_consumer = MagicMock()
        polling_delay_config = PollingDelayConfig(coin_min_polling_delay_s=23, coin_max_polling_delay_s=24)
        polling_state_storage = MagicMock()
        max_handle_transaction_tries = 5
        last_block_distance = 4

        coin_transaction_polling_service_factory(chain_query_service, logger, block_height_storage,
                                                 transaction_consumer, polling_delay_config, polling_state_storage,
                                                 max_handle_transaction_tries, last_block_distance)

        mock_transaction_polling_service.assert_called_once_with(
            chain_query_service=chain_query_service,
            logger=logger,
            block_height_storage=block_height_storage,
            transaction_consumer=transaction_consumer,
            max_polling_delay_s=polling_delay_config.coin_max_polling_delay_s,
            min_polling_delay_s=polling_delay_config.coin_min_polling_delay_s,
            polling_state_storage=polling_state_storage,
            max_handle_transaction_tries=max_handle_transaction_tries,
            last_block_distance=last_block_distance)

    @patch('waves_gateway.service.TransactionPollingService', autospec=True)
    def test_waves_transaction_polling_service_factory(self, mock_transaction_polling_service: MagicMock):
        chain_query_service = MagicMock()
        mock_transaction_polling_service_instance = MagicMock()
        mock_transaction_polling_service.return_value = mock_transaction_polling_service_instance
        logger = MagicMock()
        block_height_storage = MagicMock()
        transaction_consumer = MagicMock()
        polling_delay_config = PollingDelayConfig(waves_min_polling_delay_s=23, waves_max_polling_delay_s=24)
        polling_state_storage = MagicMock()
        max_handle_transaction_tries = 5
        last_block_distance = 5

        res = waves_transaction_polling_service_factory(
            chain_query_service, logger, block_height_storage, transaction_consumer, polling_delay_config,
            polling_state_storage, max_handle_transaction_tries, last_block_distance)

        mock_transaction_polling_service.assert_called_once_with(
            chain_query_service=chain_query_service,
            logger=logger,
            block_height_storage=block_height_storage,
            transaction_consumer=transaction_consumer,
            max_polling_delay_s=polling_delay_config.waves_max_polling_delay_s,
            min_polling_delay_s=polling_delay_config.waves_min_polling_delay_s,
            polling_state_storage=polling_state_storage,
            max_handle_transaction_tries=max_handle_transaction_tries,
            last_block_distance=last_block_distance)

        self.assertIs(res, mock_transaction_polling_service_instance)

    def test_public_configuration_factory(self):
        base_currency_name = 'Turtle Network'
        custom_currency_name = 'test_currency'
        gateway_waves_address = '7923846'
        gateway_coin_address = '732964876'
        waves_node = 'http://test_node'
        waves_asset_id = '79326478'
        waves_transaction_web_link = 'http://waves_transaction_web_link'
        waves_address_web_link = 'http://waves_address_web_link'
        coin_transaction_web_link = 'http://coin_transaction_web_link'
        coin_address_web_link = 'http://coin_address_web_link'
        web_primary_color = 'orange'

        res = public_configuration_factory(base_currency_name,custom_currency_name, gateway_waves_address, gateway_coin_address,
                                           waves_node, waves_asset_id, waves_transaction_web_link,
                                           waves_address_web_link, web_primary_color, coin_transaction_web_link,
                                           coin_address_web_link)

        self.assertEqual(res.base_currency_name, base_currency_name)
        self.assertEqual(res.custom_currency_name, custom_currency_name)
        self.assertEqual(res.gateway_waves_address, gateway_waves_address)
        self.assertEqual(res.gateway_coin_holder, gateway_coin_address)
        self.assertEqual(res.waves_node, waves_node)
        self.assertEqual(res.waves_asset_id, waves_asset_id)
        self.assertEqual(res.waves_transaction_web_link, waves_transaction_web_link)
        self.assertEqual(res.waves_address_web_link, waves_address_web_link)
        self.assertEqual(res.coin_transaction_web_link, coin_transaction_web_link)
        self.assertEqual(res.coin_address_web_link, coin_address_web_link)
        self.assertEqual(res.web_primary_color, web_primary_color)


class GatewayTest(TestCase):
    def setUp(self):
        test_dependency_map = dict()
        self._test_injector = Injector(dependency_map=test_dependency_map)

    @patch('waves_gateway.common.INJECTOR', autospec=True)
    @patch('pywaves.setNode', autospec=True)
    def test_gateway_init(self, mock_set_node: MagicMock, mock_injector: MagicMock):
        mock_injector.get.side_effect = self._test_injector.get
        mock_injector.overwrite.side_effect = self._test_injector.overwrite
        mock_injector.overwrite_if_exists.side_effect = self._test_injector.overwrite_if_exists

        coin_address_factory = MagicMock()
        coin_chain_query_service = MagicMock()
        gateway_waves_address_secret = KeyPair(public="16285786287935", secret="721365976829835")
        coin_transaction_service = MagicMock()
        gateway_coin_address_secret = KeyPair(public="79324684735", secret="734268912853")
        waves_node = 'http://waves_node'
        waves_asset_id = '72839467'
        gateway_owner_address = '7823694723'
        fee_service = MagicMock()
        coin_address_validation_service = MagicMock()
        gateway_application_service = MagicMock()
        flask_rest_controller = MagicMock()
        logging_configuration_service = MagicMock()
        mongo_database = MagicMock()

        self._test_injector.overwrite(GatewayApplicationService, gateway_application_service)
        self._test_injector.overwrite(FlaskRestController, flask_rest_controller)
        self._test_injector.overwrite(GatewayLoggingConfigurationService, logging_configuration_service)

        gateway = Gateway(
            coin_address_factory=coin_address_factory,
            coin_chain_query_service=coin_chain_query_service,
            gateway_waves_address_secret=gateway_waves_address_secret,
            coin_transaction_service=coin_transaction_service,
            gateway_coin_address_secret=gateway_coin_address_secret,
            waves_node=waves_node,
            waves_asset_id=waves_asset_id,
            gateway_owner_address=gateway_owner_address,
            fee_service=fee_service,
            only_one_transaction_receiver=False,
            coin_address_validation_service=coin_address_validation_service,
            mongo_database=mongo_database)

        gateway.set_log_level(logging.INFO)
        logging_configuration_service.set_log_level.assert_called_once_with(logging.INFO)

        gateway.run()
        gateway_application_service.run.assert_called_once_with()

        self.assertIs(self._test_injector.get(COIN_CHAIN_QUERY_SERVICE), coin_chain_query_service)
        self.assertIs(self._test_injector.get(CoinAddressFactory), coin_address_factory)
        self.assertFalse(self._test_injector.is_registered(PollingDelayConfig))
        self.assertFalse(self._test_injector.is_registered(LOGGING_HANDLER_LIST))
        self.assertFalse(self._test_injector.is_registered(POLLING_DELAY_SECONDS))
        self.assertIs(self._test_injector.get(BASE_CURRENCY_NAME), Gateway.DEFAULT_BASE_CURRENCY_NAME)
        self.assertIs(self._test_injector.get(CUSTOM_CURRENCY_NAME), Gateway.DEFAULT_CUSTOM_CURRENCY_NAME)

        self.assertIs(
            self._test_injector.get(WALLET_STORAGE_COLLECTION_NAME), Gateway.DEFAULT_WALLET_STORAGE_COLLECTION_NAME)
        self.assertIs(self._test_injector.get(MAP_STORAGE_COLLECTION_NAME), Gateway.DEFAULT_MAP_STORAGE_COLLECTION_NAME)
        self.assertIs(
            self._test_injector.get(KEY_VALUE_STORAGE_COLLECTION_NAME),
            Gateway.DEFAULT_KEY_VALUE_STORAGE_COLLECTION_NAME)
        self.assertIs(
            self._test_injector.get(TRANSACTION_ATTEMPT_LIST_STORAGE_COLLECTION_NAME),
            Gateway.DEFAULT_ATTEMPT_LIST_STORAGE_COLLECTION_NAME)
        self.assertIs(self._test_injector.get(GATEWAY_COIN_ADDRESS_SECRET), gateway_coin_address_secret)
        self.assertIs(self._test_injector.get(GATEWAY_COIN_ADDRESS), gateway_coin_address_secret.public)
        self.assertIs(self._test_injector.get(WAVES_NODE), waves_node)
        self.assertIs(self._test_injector.get(WAVES_ASSET_ID), waves_asset_id)
        self.assertIs(self._test_injector.get(WAVES_CHAIN), Gateway.DEFAULT_WAVES_CHAIN)
        self.assertIs(self._test_injector.get(ONLY_ONE_TRANSACTION_RECEIVER), False)
        self.assertFalse(self._test_injector.is_registered(COIN_TRANSACTION_WEB_LINK))
        self.assertIs(self._test_injector.get(COIN_ADDRESS_VALIDATION_SERVICE), coin_address_validation_service)
        self.assertIs(self._test_injector.get(ATTEMPT_LIST_MAX_COMPLETION_TRIES), Gateway.DEFAULT_MAX_COMPLETION_TRIES)
        self.assertIs(self._test_injector.get(GATEWAY_WAVES_ADDRESS_SECRET), gateway_waves_address_secret)
        self.assertIs(self._test_injector.get(GATEWAY_WAVES_ADDRESS), gateway_waves_address_secret.public)
        self.assertIs(self._test_injector.get(MongoDatabase), mongo_database)
