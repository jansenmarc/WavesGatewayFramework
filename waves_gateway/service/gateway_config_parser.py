"""GatewayConfigParser"""
import logging
from configparser import ConfigParser
from decimal import Decimal
from logging.handlers import RotatingFileHandler
from typing import Union, Optional, List

from waves_gateway.common import Injectable, KeyPair, InvalidConfigError, Injector, GATEWAY_COIN_ADDRESS_SECRET, \
    COIN_NODE, WAVES_NODE, GATEWAY_WAVES_ADDRESS_SECRET, GATEWAY_HOST, GATEWAY_PORT, GATEWAY_OWNER_ADDRESS, WAVES_CHAIN, \
    LOGGING_HANDLER_LIST, COIN_FEE, GATEWAY_FEE, MONGODB_HOST, MONGODB_PORT, MONGODB_DB_NAME, \
    COIN_TRANSACTION_WEB_LINK, COIN_ADDRESS_WEB_LINK, CUSTOM_CURRENCY_NAME, WAVES_ASSET_ID, WEB_PRIMARY_COLOR, \
    LOG_FILE_NAME
from waves_gateway.model import GatewayConfigFile


@Injectable(deps=[LOG_FILE_NAME])
class GatewayConfigParser(object):
    """
    May be used to parse a gateway configuration file.
    """

    def __init__(self, log_file_name: str):
        self._log_file_name = log_file_name

    def _parse_node_section(self, config_parser: ConfigParser, parsed_config: GatewayConfigFile) -> None:
        parsed_config.waves_node = config_parser.get('node', 'waves', fallback=None)
        parsed_config.coin_node = config_parser.get('node', 'coin', fallback=None)

    def _parse_number(self, config: ConfigParser, section: str, option: str) -> Union[int, Decimal]:
        """Parses a number field to an int or Decimal."""
        value = config.get(section, option)  # type: str
        if '.' in value:
            return Decimal(value)
        else:
            return int(value)

    def _parse_fee_section(self, config_parser: ConfigParser, parsed_config: GatewayConfigFile) -> None:
        parsed_config.coin_fee = self._parse_number(config_parser, 'fee', 'coin')
        parsed_config.gateway_fee = self._parse_number(config_parser, 'fee', 'gateway')

    def _parse_gateway_address_section(self, config_parser: ConfigParser, parsed_config: GatewayConfigFile):
        parsed_config.gateway_owner_address = config_parser.get('gateway_address', 'owner', fallback=None)

        gateway_waves_address_public_key = config_parser.get('gateway_address', 'waves_public_key', fallback=None)
        gateway_waves_address_private_key = config_parser.get('gateway_address', 'waves_private_key', fallback=None)
        gateway_coin_address_public_key = config_parser.get('gateway_address', 'coin_public_key', fallback=None)
        gateway_coin_address_private_key = config_parser.get(
            'gateway_address', 'coin_private_key', fallback=None)  # type: Optional[str]

        parsed_config.gateway_waves_address_secret = KeyPair(
            public=gateway_waves_address_public_key, secret=gateway_waves_address_private_key)
        parsed_config.gateway_coin_address_secret = KeyPair(
            public=gateway_coin_address_public_key, secret=gateway_coin_address_private_key)

    def _parse_mongodb_section(self, config_parser: ConfigParser, parsed_config: GatewayConfigFile) -> None:
        parsed_config.mongo_host = config_parser.get('mongodb', 'host', fallback=None)
        parsed_config.mongo_port = config_parser.getint('mongodb', 'port', fallback=None)
        parsed_config.mongo_database = config_parser.get('mongodb', 'database', fallback=None)

    def _parse_other_section(self, config_parser: ConfigParser, parsed_config: GatewayConfigFile) -> None:
        parsed_config.environment = config_parser.get('other', 'environment', fallback="prod")

        waves_chain_fallback = "mainnet"

        if parsed_config.environment == "debug":
            waves_chain_fallback = "testnet"

        parsed_config.waves_chain = config_parser.get('other', 'waves_chain', fallback=waves_chain_fallback)
        parsed_config.waves_asset_id = config_parser.get('other', 'waves_asset_id', fallback=None)

    def _parse_server_section(self, config_parser: ConfigParser, parsed_config: GatewayConfigFile):
        parsed_config.gateway_host = config_parser.get('server', 'host', fallback='localhost')
        parsed_config.gateway_port = config_parser.getint('server', 'port', fallback=5000)

    def _parse_web_section(self, config_parser: ConfigParser, parsed_config: GatewayConfigFile):
        parsed_config.transaction_web_link = config_parser.get('web', 'transaction_link', fallback=None)
        parsed_config.address_web_link = config_parser.get('web', 'address_link', fallback=None)
        parsed_config.custom_currency_name = config_parser.get('web', 'custom_currency_name', fallback=None)
        parsed_config.web_primary_color = config_parser.get('web', 'primary_color', fallback=None)

    def parse_config_file_content(self, file_content: str) -> GatewayConfigFile:
        """Parses the given config file."""
        config_parser = ConfigParser()
        config_parser.read_string(file_content)
        parsed_config = GatewayConfigFile()

        self._assert_not_old_format(config_parser)

        if config_parser.has_section('node'):
            self._parse_node_section(config_parser, parsed_config)

        if config_parser.has_section('fee'):
            self._parse_fee_section(config_parser, parsed_config)

        if config_parser.has_section('gateway_address'):
            self._parse_gateway_address_section(config_parser, parsed_config)

        if config_parser.has_section('mongodb'):
            self._parse_mongodb_section(config_parser, parsed_config)

        if config_parser.has_section('other'):
            self._parse_other_section(config_parser, parsed_config)

        if config_parser.has_section('web'):
            self._parse_web_section(config_parser, parsed_config)

        if config_parser.has_section('server'):
            self._parse_server_section(config_parser, parsed_config)

        return parsed_config

    def _assert_not_old_format(self, config_parser: ConfigParser):
        """Asserts that the old format in the ltc gateway is no longer used."""

        def assert_option_does_not_exist(section: str, option: str):
            """Raises an exception if the selected option exists."""
            if config_parser.has_section(section) and config_parser.has_option(section, option):
                raise InvalidConfigError('Detected use of option ' + option + ' in the section ' + section +
                                         '. Using ltc in a configuration file is deprecated. Please use coin instead!')

        assert_option_does_not_exist('node', 'ltc')
        assert_option_does_not_exist('fee', 'ltc')
        assert_option_does_not_exist('gateway_address', 'ltc_public_key')
        assert_option_does_not_exist('gateway_address', 'ltc_private_key')

    def parse_config_file(self, file_path: str):
        """First reads the config file and then calls parse_config_file_content with the content."""
        file = open(file_path, "r")
        return self.parse_config_file_content(file.read())

    def _init_logging_handlers(self, environment: str) -> List[logging.Handler]:
        formatter = logging.Formatter("[%(asctime)s] %(levelname)s {%(name)s} - %(message)s")
        logging_handlers = []  # type: List[logging.Handler]

        if environment == "prod":
            file_handler = RotatingFileHandler(self._log_file_name, maxBytes=10485760, backupCount=20, encoding='utf8')
            file_handler.setLevel(logging.INFO)
            file_handler.setFormatter(formatter)
            logging_handlers.append(file_handler)

            stream_handler = logging.StreamHandler()
            stream_handler.setLevel(logging.WARN)
            stream_handler.setFormatter(formatter)
            logging_handlers.append(stream_handler)
        elif environment == "debug":
            stream_handler = logging.StreamHandler()
            stream_handler.setLevel(logging.INFO)
            stream_handler.setFormatter(formatter)
            logging_handlers.append(stream_handler)
        else:
            raise Exception('Unknown environment ' + environment + '. Use prod or debug')

        return logging_handlers

    def populate_injector(self, config_file: GatewayConfigFile, injector: Injector):
        """Provides all values to the global parent injector."""
        if config_file.coin_fee is not None:
            injector.provide(COIN_FEE, config_file.coin_fee)

        if config_file.gateway_fee is not None:
            injector.provide(GATEWAY_FEE, config_file.gateway_fee)

        if config_file.gateway_coin_address_secret is not None:
            injector.provide(GATEWAY_COIN_ADDRESS_SECRET, config_file.gateway_coin_address_secret)

        if config_file.coin_node is not None:
            injector.provide(COIN_NODE, config_file.coin_node)

        if config_file.waves_node is not None:
            injector.provide(WAVES_NODE, config_file.waves_node)

        if config_file.gateway_waves_address_secret is not None:
            injector.provide(GATEWAY_WAVES_ADDRESS_SECRET, config_file.gateway_waves_address_secret)

        if config_file.gateway_host is not None:
            injector.provide(GATEWAY_HOST, config_file.gateway_host)

        if config_file.gateway_port is not None:
            injector.provide(GATEWAY_PORT, config_file.gateway_port)

        if config_file.gateway_owner_address is not None:
            injector.provide(GATEWAY_OWNER_ADDRESS, config_file.gateway_owner_address)

        if config_file.mongo_host is not None:
            injector.provide(MONGODB_HOST, config_file.mongo_host)

        if config_file.mongo_port is not None:
            injector.provide(MONGODB_PORT, config_file.mongo_port)

        if config_file.mongo_database is not None:
            injector.provide(MONGODB_DB_NAME, config_file.mongo_database)

        if config_file.transaction_web_link is not None:
            injector.provide(COIN_TRANSACTION_WEB_LINK, config_file.transaction_web_link)

        if config_file.address_web_link is not None:
            injector.provide(COIN_ADDRESS_WEB_LINK, config_file.address_web_link)

        if config_file.custom_currency_name is not None:
            injector.provide(CUSTOM_CURRENCY_NAME, config_file.custom_currency_name)

        if config_file.waves_asset_id is not None:
            injector.provide(WAVES_ASSET_ID, config_file.waves_asset_id)

        if config_file.web_primary_color is not None:
            injector.provide(WEB_PRIMARY_COLOR, config_file.web_primary_color)

        injector.provide(WAVES_CHAIN, config_file.waves_chain)
        injector.provide(LOGGING_HANDLER_LIST, self._init_logging_handlers(config_file.environment))
