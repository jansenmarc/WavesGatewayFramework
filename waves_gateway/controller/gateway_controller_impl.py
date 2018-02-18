"""
GatewayControllerImpl
"""

from doc_inherit import method_doc_inherit, class_doc_inherit  # type: ignore

from logging import Logger
from typing import Optional, List

from waves_gateway.storage.log_storage_service import LogStorageService
from waves_gateway.storage import FailedTransactionStorage, KeyValueStorage
from waves_gateway.common import WavesAddressInvalidError, InvalidTransactionIdentifier, Injectable, \
    COIN_CHAIN_QUERY_SERVICE_CONVERTER_PROXY, WAVES_CHAIN_QUERY_SERVICE_CONVERTER_PROXY
from waves_gateway.factory.coin_address_factory import CoinAddressFactory
from waves_gateway.model import MappingEntry, KeyPair, AttemptListTrigger, \
    TransactionAttemptList, AttemptListQuery, FailedTransaction
from waves_gateway.service import ChainQueryService, TransactionConsumer, \
    AddressValidationService, WavesAddressValidationService, WavesTransactionConsumerImpl, \
    CoinTransactionConsumerImpl
from waves_gateway.storage import TransactionAttemptListStorage
from waves_gateway.storage.map_storage import MapStorage
from waves_gateway.storage.wallet_storage import WalletStorage
from .gateway_controller import GatewayController


@Injectable(
    provides=GatewayController,
    deps=[
        CoinAddressFactory, Logger, MapStorage, WalletStorage, TransactionAttemptListStorage,
        WavesAddressValidationService, WAVES_CHAIN_QUERY_SERVICE_CONVERTER_PROXY,
        COIN_CHAIN_QUERY_SERVICE_CONVERTER_PROXY, CoinTransactionConsumerImpl, WavesTransactionConsumerImpl,
        FailedTransactionStorage, LogStorageService, KeyValueStorage
    ])
@class_doc_inherit
class GatewayControllerImpl(GatewayController):
    """inherit"""

    def __init__(self, coin_address_factory: CoinAddressFactory, logger: Logger, map_storage: MapStorage,
                 wallet_storage: WalletStorage, attempt_list_storage: TransactionAttemptListStorage,
                 waves_address_validation_service: AddressValidationService,
                 waves_chain_query_service: ChainQueryService, coin_chain_query_service: ChainQueryService,
                 coin_transaction_consumer: TransactionConsumer, waves_transaction_consumer: TransactionConsumer,
                 failed_transaction_storage: FailedTransactionStorage, log_storage_service: LogStorageService,
                 key_value_storage: KeyValueStorage) -> None:
        self._coin_address_factory = coin_address_factory
        self._map_storage = map_storage
        self._wallet_storage = wallet_storage
        self._logger = logger.getChild('GatewayControllerImpl')
        self._attempt_list_storage = attempt_list_storage
        self._waves_address_validation_service = waves_address_validation_service
        self._waves_chain_query_service = waves_chain_query_service
        self._coin_chain_query_service = coin_chain_query_service
        self._coin_transaction_consumer = coin_transaction_consumer
        self._waves_transaction_consumer = waves_transaction_consumer
        self._failed_transaction_storage = failed_transaction_storage
        self._log_storage_service = log_storage_service
        self._key_value_storage = key_value_storage

    @method_doc_inherit
    def check_waves_transaction(self, tx: str) -> None:
        transaction = self._waves_chain_query_service.get_transaction_by_tx(tx)

        if transaction is None:
            raise InvalidTransactionIdentifier()

        if self._waves_transaction_consumer.filter_transaction(transaction):
            self._waves_transaction_consumer.handle_transaction(transaction)

    @method_doc_inherit
    def check_coin_transaction(self, tx: str) -> None:
        transaction = self._coin_chain_query_service.get_transaction_by_tx(tx)

        if transaction is None:
            raise InvalidTransactionIdentifier()

        if self._coin_transaction_consumer.filter_transaction(transaction):
            self._coin_transaction_consumer.handle_transaction(transaction)

    @method_doc_inherit
    def validate_waves_address(self, address: str) -> bool:
        """inherit"""
        return self._waves_address_validation_service.validate_address(address)

    @method_doc_inherit
    def create_address(self, waves_address: str) -> str:
        """inherit"""
        self._logger.debug("Client requested coin address for waves address '%s'", waves_address)

        if not self._waves_address_validation_service.validate_address(waves_address):
            raise WavesAddressInvalidError()

        if self._map_storage.waves_address_exists(waves_address):
            coin_address = self._map_storage.get_coin_address_by_waves_address(waves_address)
            self._logger.debug("Found associated coin_address '%s'", coin_address)
            return coin_address
        else:
            create_address_result = self._coin_address_factory.create_address()

            if isinstance(create_address_result, str):
                mapping = MappingEntry(waves_address, create_address_result)
                self._map_storage.safely_save_mapping(mapping)
                self._logger.info("Created new mapping '%s'", str(mapping))
                return create_address_result
            elif isinstance(create_address_result, KeyPair):
                mapping = MappingEntry(waves_address, create_address_result.public)
                self._wallet_storage.safely_save_address_secret(create_address_result)
                self._map_storage.safely_save_mapping(mapping)
                self._logger.info("Created new mapping '%s'", str(mapping))

                return create_address_result.public
            else:
                raise TypeError('Result of create_address is neither a CoinAddress nor a CoinAddressSecret')

    @method_doc_inherit
    def get_attempt_list_by_id(self, attempt_list_id: str) -> Optional[TransactionAttemptList]:
        return self._attempt_list_storage.find_by_attempt_list_id(attempt_list_id)

    @method_doc_inherit
    def get_block_heights(self):
        last_checked_coin_block_height = self._key_value_storage.get_last_checked_coin_block_height()
        last_checked_waves_block_height = self._key_value_storage.get_last_checked_waves_block_height()

        return {
            "last_checked_coin_block_height": last_checked_coin_block_height,
            "last_checked_waves_block_height": last_checked_waves_block_height
        }

    @method_doc_inherit
    def get_average_attempt_list_tries(self):
        return self._attempt_list_storage.get_average_attempt_list_tries()

    def get_failed_transactions(self):
        return self._failed_transaction_storage.get_failed_transactions()

    def get_log_messages(self):
        return self._log_storage_service.get_messages()

    @method_doc_inherit
    def query_attempt_lists(self, query: AttemptListQuery) -> List[TransactionAttemptList]:
        return self._attempt_list_storage.query_attempt_lists(query)

    @method_doc_inherit
    def get_attempt_list_by_trigger(self, trigger: AttemptListTrigger) -> Optional[TransactionAttemptList]:
        return self._attempt_list_storage.find_by_trigger(trigger)

    @method_doc_inherit
    def trigger_attemptlist_retry(self, id: str) -> str:
        attemptlist = self._attempt_list_storage.find_by_attempt_list_id(id)
        if (attemptlist):
            attemptlist.reset_tries()
            self._attempt_list_storage.update_attempt_list(attemptlist)
            return ''
        else:
            return None
