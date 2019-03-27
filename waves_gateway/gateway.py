"""
Gateway
"""

import logging
import os
from typing import Optional, List

import flask  # type: ignore
import pywaves  # type: ignore

from flask import Flask

from waves_gateway.service import COIN_TRANSACTION_POLLING_SERVICE, \
    WAVES_TRANSACTION_POLLING_SERVICE, WavesTransactionConsumerImpl, CoinTransactionConsumerImpl, IntegerConverterService
from waves_gateway.common import Factory, LOGGING_HANDLER_LIST, MANAGED_LOGGER_LIST, POLLING_DELAY_SECONDS, \
    CUSTOM_CURRENCY_NAME, GATEWAY_OWNER_ADDRESS, WALLET_STORAGE_COLLECTION_NAME, MAP_STORAGE_COLLECTION_NAME, \
    KEY_VALUE_STORAGE_COLLECTION_NAME, TRANSACTION_ATTEMPT_LIST_STORAGE_COLLECTION_NAME, GATEWAY_COIN_ADDRESS_SECRET, \
    GATEWAY_COIN_ADDRESS, WAVES_NODE, WAVES_ASSET_ID, WAVES_CHAIN, ONLY_ONE_TRANSACTION_RECEIVER, \
    COIN_TRANSACTION_WEB_LINK, WAVES_TRANSACTION_WEB_LINK, COIN_ADDRESS_WEB_LINK, WAVES_ADDRESS_WEB_LINK, \
    ATTEMPT_LIST_MAX_COMPLETION_TRIES, GATEWAY_WAVES_ADDRESS_SECRET, GATEWAY_WAVES_ADDRESS, NUM_ATTEMPT_LIST_WORKERS, \
    GATEWAY_HOST, GATEWAY_PORT, WALLET_STORAGE_COLLECTION, MAP_STORAGE_COLLECTION, KEY_VALUE_STORAGE_COLLECTION, \
    TRANSACTION_ATTEMPT_LIST_STORAGE_COLLECTION, GATEWAY_PYWAVES_ADDRESS, COIN_CHAIN_QUERY_SERVICE_CONVERTER_PROXY, \
    WAVES_CHAIN_QUERY_SERVICE_CONVERTER_PROXY, FLASK_NAME, COIN_MAX_HANDLE_TRANSACTION_TRIES, \
    WAVES_MAX_HANDLE_TRANSACTION_TRIES, WAVES_LAST_BLOCK_DISTANCE, COIN_LAST_BLOCK_DISTANCE, WEB_PRIMARY_COLOR, \
    WAVES_CHAIN_ID
from waves_gateway.model import PollingDelayConfig
from waves_gateway.factory import CoinAddressFactory

import waves_gateway.common as common
import waves_gateway.controller as controller
import waves_gateway.model as model
import waves_gateway.service as service
import waves_gateway.storage as storage
import waves_gateway.factory as factory
from pymongo.database import Database as MongoDatabase  # type: ignore

from waves_gateway.model import PublicConfiguration
from waves_gateway.service import COIN_CHAIN_QUERY_SERVICE, COIN_ADDRESS_VALIDATION_SERVICE, COIN_TRANSACTION_SERVICE, COIN_INTEGER_CONVERTER_SERVICE, \
    ASSET_INTEGER_CONVERTER_SERVICE
from waves_gateway.storage import CoinBlockHeightStorageProxyImpl, WavesBlockHeightStorageProxyImpl, CoinPollingStateStorageProxyImpl, WavesPollingStateStorageProxyImpl, PollingStateStorageProxy


@Factory(Flask, deps=[FLASK_NAME])
def flask_factory(flask_name: str):
    """Configures the flask instance."""
    directory, file = os.path.split(os.path.realpath(__file__))
    return flask.Flask(flask_name, static_folder=os.path.join(directory, 'static'))


@Factory(logging.Logger, deps=[Flask, LOGGING_HANDLER_LIST, MANAGED_LOGGER_LIST])
def logger_factory(flask: Flask, logging_handlers: List[logging.Handler], managed_loggers: List[logging.Logger]):
    """Creates the major logger instance of the Gateway."""
    logger = flask.logger
    logger.setLevel(logging.DEBUG)

    for handler in logging_handlers:
        for managed_logger in managed_loggers:
            managed_logger.addHandler(handler)

        logger.addHandler(handler)

    return logger


@Factory(LOGGING_HANDLER_LIST, weak=True)
def logging_handlers_factory():
    """Provides a default list of logging handlers that log to the console."""
    logging_handlers = list()
    formatter = logging.Formatter("[%(asctime)s] %(levelname)s {%(name)s} - %(message)s")

    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.DEBUG)
    stream_handler.setFormatter(formatter)

    logging_handlers.append(stream_handler)
    return logging_handlers


@Factory(PollingDelayConfig, opt_deps=[POLLING_DELAY_SECONDS], weak=True)
def polling_delay_config_factory(polling_delay_s: Optional[float]):
    """
    Provides a default PollingDelayConfig.
    If the old API (polling_delay_s) is used, the PollingDelayConfig is constructed using the polling_delay_s value.
    """
    if polling_delay_s is None:
        return model.PollingDelayConfig()
    elif polling_delay_s is not None:
        return model.PollingDelayConfig.from_single_polling_delay(polling_delay_s)
    else:
        raise common.InvalidConfigError(
            'It is not possible to specify both a fixed polling_delay_s and a dynamic PollingDelayConfig.')


@Factory(
    TRANSACTION_ATTEMPT_LIST_STORAGE_COLLECTION, deps=[TRANSACTION_ATTEMPT_LIST_STORAGE_COLLECTION_NAME, MongoDatabase])
@Factory(WALLET_STORAGE_COLLECTION, deps=[WALLET_STORAGE_COLLECTION_NAME, MongoDatabase])
@Factory(MAP_STORAGE_COLLECTION, deps=[MAP_STORAGE_COLLECTION_NAME, MongoDatabase])
@Factory(KEY_VALUE_STORAGE_COLLECTION, deps=[KEY_VALUE_STORAGE_COLLECTION_NAME, MongoDatabase])
def collection_factory(collection_name: str, database: MongoDatabase):
    """Creates a new collection with the given name."""
    return database.get_collection(collection_name)


@Factory(GATEWAY_PYWAVES_ADDRESS, deps=[GATEWAY_WAVES_ADDRESS_SECRET, WAVES_NODE, WAVES_CHAIN], opt_deps=[WAVES_CHAIN_ID])
def gateway_pywaves_address(gateway_waves_address_secret: model.KeyPair, waves_node: str, waves_chain: str, waves_chain_id: Optional[str] = None):
    """Creates an address instance from the pywaves library that represents the Gateway waves address."""
    pywaves.setNode(waves_node, waves_chain, waves_chain_id)
    address = pywaves.Address(privateKey=gateway_waves_address_secret.secret)
    if address.address != gateway_waves_address_secret.public:
        raise ValueError("Gateway account private key doesn't match the address provided")
    return address


@Factory(
    COIN_TRANSACTION_POLLING_SERVICE,
    deps=[
        COIN_CHAIN_QUERY_SERVICE_CONVERTER_PROXY, logging.Logger, CoinBlockHeightStorageProxyImpl,
        CoinTransactionConsumerImpl, model.PollingDelayConfig, CoinPollingStateStorageProxyImpl,
        COIN_MAX_HANDLE_TRANSACTION_TRIES, COIN_LAST_BLOCK_DISTANCE
    ])
def coin_transaction_polling_service_factory(coin_chain_query_service_converter_proxy, logger,
                                             coin_block_height_storage_proxy, coin_transaction_consumer,
                                             polling_delay_config, polling_state_storage: PollingStateStorageProxy,
                                             max_handle_transaction_tries: int, last_block_distance):
    """Creates a TransactionPollingService instance with the necessary dependencies for the custom cryptocurrency."""
    return service.TransactionPollingService(
        chain_query_service=coin_chain_query_service_converter_proxy,
        logger=logger,
        block_height_storage=coin_block_height_storage_proxy,
        transaction_consumer=coin_transaction_consumer,
        max_polling_delay_s=polling_delay_config.coin_max_polling_delay_s,
        min_polling_delay_s=polling_delay_config.coin_min_polling_delay_s,
        max_handle_transaction_tries=max_handle_transaction_tries,
        polling_state_storage=polling_state_storage,
        last_block_distance=last_block_distance)


@Factory(
    WAVES_TRANSACTION_POLLING_SERVICE,
    deps=[
        WAVES_CHAIN_QUERY_SERVICE_CONVERTER_PROXY, logging.Logger, WavesBlockHeightStorageProxyImpl,
        WavesTransactionConsumerImpl, model.PollingDelayConfig, WavesPollingStateStorageProxyImpl,
        WAVES_MAX_HANDLE_TRANSACTION_TRIES, WAVES_LAST_BLOCK_DISTANCE
    ])
def waves_transaction_polling_service_factory(waves_chain_query_service_converter_proxy, logger,
                                              waves_block_height_storage_proxy, waves_transaction_consumer,
                                              polling_delay_config, polling_state_storage: PollingStateStorageProxy,
                                              max_handle_transaction_tries: int, last_block_distance: int):
    """Creates a TransactionPollingService instance with the necessary dependencies for Waves."""
    return service.TransactionPollingService(
        chain_query_service=waves_chain_query_service_converter_proxy,
        logger=logger,
        block_height_storage=waves_block_height_storage_proxy,
        transaction_consumer=waves_transaction_consumer,
        max_polling_delay_s=polling_delay_config.waves_max_polling_delay_s,
        min_polling_delay_s=polling_delay_config.waves_min_polling_delay_s,
        max_handle_transaction_tries=max_handle_transaction_tries,
        polling_state_storage=polling_state_storage,
        last_block_distance=last_block_distance)


@Factory(
    PublicConfiguration,
    deps=[
        CUSTOM_CURRENCY_NAME, GATEWAY_WAVES_ADDRESS, GATEWAY_COIN_ADDRESS, WAVES_NODE, WAVES_ASSET_ID,
        WAVES_TRANSACTION_WEB_LINK, WAVES_ADDRESS_WEB_LINK, WEB_PRIMARY_COLOR
    ],
    opt_deps=[COIN_TRANSACTION_WEB_LINK, COIN_ADDRESS_WEB_LINK])
def public_configuration_factory(custom_currency_name: str,
                                 gateway_waves_address: str,
                                 gateway_coin_address: str,
                                 waves_node: str,
                                 waves_asset_id: str,
                                 waves_transaction_web_link: str,
                                 waves_address_web_link: str,
                                 web_primary_color: str,
                                 coin_transaction_web_link: Optional[str] = None,
                                 coin_address_web_link: Optional[str] = None):
    """Creates a constant global configuration instance that may be provided to the client."""
    return model.PublicConfiguration(
        custom_currency_name=custom_currency_name,
        gateway_waves_address=gateway_waves_address,
        gateway_coin_address=gateway_coin_address,
        waves_node=waves_node,
        waves_asset_id=waves_asset_id,
        waves_transaction_web_link=waves_transaction_web_link,
        waves_address_web_link=waves_address_web_link,
        coin_transaction_web_link=coin_transaction_web_link,
        coin_address_web_link=coin_address_web_link,
        web_primary_color=web_primary_color)


@Factory(COIN_INTEGER_CONVERTER_SERVICE, weak=True)
def coin_integer_converter_service_factory():
    """Provides the default IntegerConverterService for the custom cryptocurrency."""
    return IntegerConverterService()


@Factory(ASSET_INTEGER_CONVERTER_SERVICE, weak=True)
def asset_integer_converter_service_factory():
    """Provides the default IntegerConverterService for the asset."""
    return IntegerConverterService()


@Factory(WAVES_ADDRESS_WEB_LINK, weak=True, deps=[WAVES_CHAIN])
def waves_address_web_link_factory(waves_chain: str):
    """Provides default value for WAVES_ADDRESS_WEB_LINK depending on WAVES_CHAIN."""
    if waves_chain == 'testnet':
        return 'https://testnet.wavesexplorer.com/address/{{address}}'
    else:
        return 'https://wavesexplorer.com/address/{{address}}'


@Factory(WAVES_TRANSACTION_WEB_LINK, weak=True, deps=[WAVES_CHAIN])
def waves_transaction_web_link_factory(waves_chain: str):
    """Provides default value for WAVES_TRANSACTION_WEB_LINK depending on WAVES_CHAIN."""
    if waves_chain == 'testnet':
        return 'https://testnet.wavesexplorer.com/tx/{{tx}}'
    else:
        return 'https://wavesexplorer.com/tx/{{tx}}'


class Gateway(object):
    """
    Provides the configuration for the Gateway.
    When setting up the Gateway for a specific currency, use this class
    to collect the information and call the run method of the instance.

    The constructor has specific parameters that are marked as required.
    Those parameters must be provided for a minimum configuration.
    To provide those instances, the abstract classes have to be implemented.
    Then, create one instance per each and overhand them to the gateway.
    Provided instances should not have any dependencies on other instances managed by this class.
    But, if strongly necessary they may use the public instances provided by an instance of the Gateway class.

    Alongside the required parameters, there are additional optional parameters that may be provided.
    The Gateway is capable of filling them with default implementations listed in the constructor documentation.
    But, if an default implementation is not suitable, it may be replaced by handing over a different implementation
    to the Gateway. If so, this implementation will be used and no instance of an default implementation will
    be created.

    The resulting Gateway instance is not running. Which means that the pollers are not started.
    To start those pollers call the run method on the Gateway instance.
    Furthermore, it is possible to stop the pollers by calling cancel on the Gateway. But, it should generally
    not be necessary to do so.
    """

    DEFAULT_FLASK_NAME = 'waves-gw'
    DEFAULT_CUSTOM_CURRENCY_NAME = 'Custom Currency'
    DEFAULT_POLLING_DELAY = 0
    DEFAULT_WAVES_POLLING_DELAY = 0
    DEFAULT_HOSTNAME = 'localhost'
    DEFAULT_PORT = 5000
    DEFAULT_WAVES_CHAIN = 'mainnet'
    DEFAULT_NUM_ATTEMPT_LIST_WORKERS = 1
    DEFAULT_MAX_COMPLETION_TRIES = 30
    DEFAULT_WALLET_STORAGE_COLLECTION_NAME = 'wallet'
    DEFAULT_MAP_STORAGE_COLLECTION_NAME = 'mapping'
    DEFAULT_ATTEMPT_LIST_STORAGE_COLLECTION_NAME = 'attempt_list'
    DEFAULT_KEY_VALUE_STORAGE_COLLECTION_NAME = 'key_value'
    DEFAULT_COIN_MAX_HANDLE_TRANSACTION_TRIES = 5
    DEFAULT_WAVES_MAX_HANDLE_TRANSACTION_TRIES = 5
    DEFAULT_COIN_LAST_BLOCK_DISTANCE = 0
    DEFAULT_WAVES_LAST_BLOCK_DISTANCE = 1
    DEFAULT_WEB_PRIMARY_COLOR = '#2196f3'

    def _init_managed_loggers(self, managed_loggers: List[str]) -> None:
        res = list()  # type: List[logging.Logger]

        if managed_loggers is None:
            managed_loggers = list()

        if "werkzeug" not in managed_loggers:
            managed_loggers.append("werkzeug")

        for logger_name in managed_loggers:
            logger_instance = logging.getLogger(logger_name)
            logger_instance.handlers = []
            logger_instance.setLevel(logging.DEBUG)
            res.append(logger_instance)

        self._injector.overwrite(MANAGED_LOGGER_LIST, res)

    def __init__(self,
                 coin_address_factory: factory.CoinAddressFactory,
                 coin_chain_query_service: service.ChainQueryService,
                 gateway_waves_address_secret: model.KeyPair,
                 coin_transaction_service: service.TransactionService,
                 gateway_coin_address_secret: model.KeyPair,
                 waves_node: str,
                 waves_asset_id: str,
                 gateway_owner_address: str,
                 fee_service: service.FeeService,
                 coin_address_validation_service: service.AddressValidationService,
                 coin_transaction_web_link: Optional[str] = None,
                 waves_transaction_web_link: Optional[str] = None,
                 coin_address_web_link: Optional[str] = None,
                 waves_address_web_link: Optional[str] = None,
                 coin_integer_converter_service: Optional[service.IntegerConverterService] = None,
                 asset_integer_converter_service: Optional[service.IntegerConverterService] = None,
                 waves_chain=DEFAULT_WAVES_CHAIN,
                 only_one_transaction_receiver: bool = False,
                 custom_currency_name: str = DEFAULT_CUSTOM_CURRENCY_NAME,
                 logging_handlers: Optional[list] = None,
                 managed_loggers: List[str] = list(),
                 attempt_list_max_completion_tries: int = DEFAULT_MAX_COMPLETION_TRIES,
                 host: str = DEFAULT_HOSTNAME,
                 port: int = DEFAULT_PORT,
                 num_attempt_list_workers=DEFAULT_NUM_ATTEMPT_LIST_WORKERS,
                 polling_delay_s: Optional[float] = None,
                 polling_delay_config: Optional[model.PollingDelayConfig] = None,
                 transaction_attempt_list_storage_collection_name=DEFAULT_ATTEMPT_LIST_STORAGE_COLLECTION_NAME,
                 wallet_storage_collection_name: str = DEFAULT_WALLET_STORAGE_COLLECTION_NAME,
                 map_storage_collection_name: str = DEFAULT_MAP_STORAGE_COLLECTION_NAME,
                 key_value_storage_collection_name: str = DEFAULT_KEY_VALUE_STORAGE_COLLECTION_NAME,
                 key_value_storage: Optional[storage.KeyValueStorage] = None,
                 map_storage: Optional[storage.MapStorage] = None,
                 wallet_storage: Optional[storage.WalletStorage] = None,
                 mongo_database: Optional[MongoDatabase] = None,
                 gateway_controller: Optional[controller.GatewayController] = None,
                 coin_max_handle_transaction_tries: int = DEFAULT_COIN_MAX_HANDLE_TRANSACTION_TRIES,
                 waves_max_handle_transaction_tries: int = DEFAULT_WAVES_MAX_HANDLE_TRANSACTION_TRIES,
                 coin_last_block_distance: int = DEFAULT_COIN_LAST_BLOCK_DISTANCE,
                 waves_last_block_distance: int = DEFAULT_WAVES_LAST_BLOCK_DISTANCE,
                 web_primary_color: str = DEFAULT_WEB_PRIMARY_COLOR,
                 waves_chain_id: Optional[str] = None
                 ) -> None:
        """
        Creates a new Gateway instance.

        :param coin_address_factory:
            Instance of an CoinAddressFactory that must be provided.
            Provides the functionality to create new addresses of the custom currency.

        :param coin_chain_query_service:
            This must be an instance of a CoinChainQuery service sub-class.
            It allows the gateway to perform certain queries on the Blockchain of the custom currency.

        :param gateway_waves_address_secret:
            Represents the address of the Gateway in Waves.

        :param coin_transaction_service:
            Implements the functionality to perform transactions in the custom currency.

        :param waves_node:
            Sets the Waves node that shall be used, for example: http://5.189.136.6:6869.

        :param waves_asset_id:
            The identifier for the Waves Asset that shall be used.

        :param gateway_owner_address:
            The coin address of the person who owns the Gateway; runs the server.
            A small amount of coins will be transferred to this address every time the Gateway performs
            a Waves transaction. The concrete amount is calculated based on the
            given percentage 'gateway_owner_waves_fee_percentage'.

        :param fee_service:

        :param only_one_transaction_receiver:
            Defines whether the custom cryptocurrency supports only one receiver of a transaction.

        :param waves_chain:
            Allows to configure the waves_chain to be used. This can either be 'mainnet' or 'testnet'.
            By default 'mainnet' will be used.

        :param custom_currency_name:
            Name that shall be used when something regarding the custom currency is displayed.
            Major use is in the Web App.

        :param logging_handlers:
            An array of logging.Handler implementations to use. By default a single StreamHandler
            is used with an DEBUG level.

        :param managed_loggers:
            Allows to process other logger inputs. Uses logging.getLogger with the given names to
            fetch those additional loggers.

        :param host
            The hostname to be used for the Web Server. Default is localhost.

        :param port
            The port to be used for the Web Server. Default is 5000.

        :param polling_delay_s:
            Optional parameter that allows to specify the delay in seconds between polling
            schedules of the block poller calls.

        :param wallet_storage_collection_name:
            May overwrite the collection name of the wallet storage in the MongoDB.
            This has no effect, if a custom storage implementation is used.

        :param map_storage_collection_name:
            May overwrite the collection name of the map storage in the MongoDB.
            This has no effect, if a custom storage implementation is used.

        :param key_value_storage_collection_name:
            May overwrite the collection name of the key_value storage in the MongoDB.
            This has no effect, if a custom storage implementation is used.

        :param key_value_storage:
            Is used to store key-value pairs. Defaults to an MongoDB implementation.

        :param map_storage:
            Stores the associations between custom currency addresses and Waves addresses.

        :param wallet_storage:
            Stores the secrets of the private keys created by the CoinAddressFactory.

        :param mongo_database:
            This is marked as Optional, but is required if no custom storage implementations are used.
            This must be a valid instance of a MongoDB database of the PyMongo framework.

        :param gateway_controller:
            This is an instance of the external API of the Gateway. For example,
            the Gateway offers the possibility to create an ReST interface by specifying a Flask instance.
            Please take a look at the flask parameter description for more information.
            The auto-generated ReST API uses this controller in the background to process the incoming requests.
            The default implementation should be sufficient for most use cases, but it may be overridden here.

        :param gateway_coin_address_secret:
            This is the major Gateway address for storing coins of the custom cryptocurrency.

        :param coin_last_block_distance:
            This may be used to prevent a check of the highest block.

        :param waves_last_block_distance:
            This may be used to prevent a check of the highest block.

        """
        self._injector = common.INJECTOR
        self._injector.overwrite(CoinAddressFactory, coin_address_factory)
        self._injector.overwrite(COIN_CHAIN_QUERY_SERVICE, coin_chain_query_service)
        self._injector.overwrite_if_exists(LOGGING_HANDLER_LIST, logging_handlers)
        self._injector.overwrite_if_exists(POLLING_DELAY_SECONDS, polling_delay_s)
        self._injector.overwrite_if_exists(PollingDelayConfig, polling_delay_config)
        self._injector.overwrite(CUSTOM_CURRENCY_NAME, custom_currency_name)
        self._injector.overwrite(GATEWAY_OWNER_ADDRESS, gateway_owner_address)
        self._injector.overwrite(WALLET_STORAGE_COLLECTION_NAME, wallet_storage_collection_name)
        self._injector.overwrite(MAP_STORAGE_COLLECTION_NAME, map_storage_collection_name)
        self._injector.overwrite(KEY_VALUE_STORAGE_COLLECTION_NAME, key_value_storage_collection_name)
        self._injector.overwrite(TRANSACTION_ATTEMPT_LIST_STORAGE_COLLECTION_NAME,
                                 transaction_attempt_list_storage_collection_name)
        self._injector.overwrite(GATEWAY_COIN_ADDRESS_SECRET, gateway_coin_address_secret)
        self._injector.overwrite(GATEWAY_COIN_ADDRESS, gateway_coin_address_secret.public)
        self._injector.overwrite(WAVES_NODE, waves_node)
        self._injector.overwrite(WAVES_ASSET_ID, waves_asset_id)
        self._injector.overwrite(WAVES_CHAIN, waves_chain)
        self._injector.overwrite(ONLY_ONE_TRANSACTION_RECEIVER, only_one_transaction_receiver)
        self._injector.overwrite_if_exists(COIN_TRANSACTION_WEB_LINK, coin_transaction_web_link)
        self._injector.overwrite_if_exists(WAVES_TRANSACTION_WEB_LINK, waves_transaction_web_link)
        self._injector.overwrite_if_exists(COIN_ADDRESS_WEB_LINK, coin_address_web_link)
        self._injector.overwrite_if_exists(WAVES_ADDRESS_WEB_LINK, waves_address_web_link)
        self._injector.overwrite(COIN_ADDRESS_VALIDATION_SERVICE, coin_address_validation_service)
        self._injector.overwrite(ATTEMPT_LIST_MAX_COMPLETION_TRIES, attempt_list_max_completion_tries)
        self._injector.overwrite(GATEWAY_WAVES_ADDRESS_SECRET, gateway_waves_address_secret)
        self._injector.overwrite(GATEWAY_WAVES_ADDRESS, gateway_waves_address_secret.public)
        self._injector.overwrite_if_exists(MongoDatabase, mongo_database)
        self._injector.overwrite_if_exists(storage.KeyValueStorage, key_value_storage)
        self._injector.overwrite_if_exists(storage.MapStorage, map_storage)
        self._injector.overwrite_if_exists(storage.WalletStorage, wallet_storage)
        self._injector.overwrite_if_exists(COIN_INTEGER_CONVERTER_SERVICE, coin_integer_converter_service)
        self._injector.overwrite_if_exists(ASSET_INTEGER_CONVERTER_SERVICE, asset_integer_converter_service)
        self._injector.overwrite(service.FeeService, fee_service)
        self._injector.overwrite(COIN_TRANSACTION_SERVICE, coin_transaction_service)
        self._injector.overwrite_if_exists(controller.GatewayController, gateway_controller)
        self._injector.overwrite(NUM_ATTEMPT_LIST_WORKERS, num_attempt_list_workers)
        self._injector.overwrite(GATEWAY_HOST, host)
        self._injector.overwrite(GATEWAY_PORT, port)
        self._injector.overwrite(FLASK_NAME, Gateway.DEFAULT_FLASK_NAME)
        self._injector.overwrite(COIN_MAX_HANDLE_TRANSACTION_TRIES, coin_max_handle_transaction_tries)
        self._injector.overwrite(WAVES_MAX_HANDLE_TRANSACTION_TRIES, waves_max_handle_transaction_tries)
        self._injector.overwrite(COIN_LAST_BLOCK_DISTANCE, coin_last_block_distance)
        self._injector.overwrite(WAVES_LAST_BLOCK_DISTANCE, waves_last_block_distance)
        self._injector.overwrite(WEB_PRIMARY_COLOR, web_primary_color)
        self._injector.overwrite_if_exists(WAVES_CHAIN_ID, waves_chain_id)

        self._init_managed_loggers(managed_loggers)

        self._application_service = self._injector.get(
            service.GatewayApplicationService)  # type: service.GatewayApplicationService

        self._flask_rest_controller = self._injector.get(controller.FlaskRestController)
        self._logging_service = self._injector.get(
            service.GatewayLoggingConfigurationService)  # type: service.GatewayLoggingConfigurationService

        self.set_log_level = self._logging_service.set_log_level
        self.run = self._application_service.run
