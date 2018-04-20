"""
Waves Gateway Library
========================

Contains tools to create a new Waves Cryptocurrency Gateway.
It is recommended to call gevent.monkey.patch_all() at the very beginning of the application
as this library uses gevent for non-blocking io.
"""

import gevent.monkey
gevent.monkey.patch_all()

import gevent.hub
gevent.hub.Hub.NOT_ERROR = (Exception, )

from waves_gateway.factory import CoinAddressFactory
from waves_gateway.model import KeyPair, \
    TransactionAttemptReceiver, \
    TransactionAttempt, Transaction, TransactionReceiver, TransactionSender, PollingDelayConfig, GatewayConfigFile
from .gateway import Gateway, run, define
from waves_gateway.service import ChainQueryService, TransactionService, IntegerConverterService, \
    FeeService, ConstantFeeServiceImpl, AddressValidationService, COIN_INTEGER_CONVERTER_SERVICE, \
    COIN_TRANSACTION_SERVICE, COIN_CHAIN_QUERY_SERVICE, COIN_ADDRESS_VALIDATION_SERVICE,\
    GatewayConfigParser, GatewayApplicationService, GatewayLoggingConfigurationService, \
    COIN_TRANSACTION_POLLING_SERVICE
from waves_gateway.storage import WalletStorage, MapStorage, KeyValueStorage
from waves_gateway.common import convert_to_int, convert_to_decimal, ProxyGuard, InvalidTransactionIdentifier,\
    InjectionToken, ChildInjectable as Injectable, ChildFactory as Factory, CHILD_INJECTOR as INJECTOR, Injector, InjectorError, \
    Token, COIN_NODE, CUSTOM_CURRENCY_NAME, WAVES_ASSET_ID, ProxyFactory, GATEWAY_WAVES_ADDRESS_SECRET, GATEWAY_OWNER_ADDRESS, \
    GATEWAY_COIN_ADDRESS_SECRET, MANAGED_LOGGER_LIST, WAVES_NODE, POLLING_DELAY_SECONDS, GATEWAY_FEE, COIN_FEE, \
    WAVES_FEE, LOG_FILE_NAME

from typing import NewType

CoinAddress = NewType('CoinAddress', str)
WavesAddress = NewType('WavesAddress', str)

WavesAddressSecret = NewType('WavesAddressSecret', KeyPair)
CoinAddressSecret = NewType('CoinAddressSecret', KeyPair)

CoinTransactionIdentifier = NewType('CoinTransactionIdentifier', str)
WavesTransactionIdentifier = NewType('WavesTransactionIdentifier', str)

CoinBlockHeight = NewType('CoinBlockHeight', int)
WavesBlockHeight = NewType('WavesBlockHeight', int)

WavesTransaction = NewType('WavesTransaction', Transaction)
CoinTransaction = NewType('CoinTransaction', Transaction)

CoinAmount = NewType('CoinAmount', int)
