import unittest
from typing import cast
from unittest.mock import MagicMock

import logging

from waves_gateway.service import AddressValidationService, ChainQueryService, TransactionConsumer

from waves_gateway.storage import MapStorage, WalletStorage, TransactionAttemptListStorage, FailedTransactionStorage, \
    LogStorageService, KeyValueStorage
from waves_gateway.common import WavesAddressInvalidError, InvalidTransactionIdentifier
from waves_gateway.controller import GatewayControllerImpl
from waves_gateway.factory import CoinAddressFactory
from waves_gateway.model import MappingEntry, AttemptListQuery, AttemptListTrigger, KeyPair


class GatewayControllerImplTest(unittest.TestCase):
    def setUp(self):
        self._coin_address_factory = MagicMock()
        self._map_storage = MagicMock()
        self._wallet_storage = MagicMock()
        self._logger = MagicMock()
        self._attempt_list_storage = MagicMock()
        self._waves_address_validation_service = MagicMock()
        self._coin_chain_query_service = MagicMock()
        self._coin_transaction_consumer = MagicMock()
        self._waves_chain_query_service = MagicMock()
        self._waves_transaction_consumer = MagicMock()
        self._failed_transaction_storage = MagicMock()
        self._log_storage_service = MagicMock()
        self._key_value_storage = MagicMock()

        self._gateway_controller = GatewayControllerImpl(
            coin_address_factory=cast(CoinAddressFactory, self._coin_address_factory),
            map_storage=cast(MapStorage, self._map_storage),
            wallet_storage=cast(WalletStorage, self._wallet_storage),
            logger=cast(logging.Logger, self._logger),
            attempt_list_storage=cast(TransactionAttemptListStorage, self._attempt_list_storage),
            waves_address_validation_service=cast(AddressValidationService, self._waves_address_validation_service),
            coin_chain_query_service=cast(ChainQueryService, self._coin_chain_query_service),
            coin_transaction_consumer=cast(TransactionConsumer, self._coin_transaction_consumer),
            waves_chain_query_service=cast(ChainQueryService, self._waves_chain_query_service),
            waves_transaction_consumer=cast(TransactionConsumer, self._waves_transaction_consumer),
            failed_transaction_storage=cast(FailedTransactionStorage, self._failed_transaction_storage),
            log_storage_service=cast(LogStorageService, self._log_storage_service),
            key_value_storage=cast(KeyValueStorage, self._key_value_storage))

    def test_create_address_already_exists(self):
        mock_waves_address = "72936587"
        mock_coin_address = "8120743689"

        self._waves_address_validation_service.validate_address.return_value = True
        self._map_storage.waves_address_exists.return_value = True
        self._map_storage.get_coin_address_by_waves_address.return_value = mock_coin_address

        res = self._gateway_controller.create_address(mock_waves_address)

        self._map_storage.waves_address_exists.assert_called_once_with(mock_waves_address)
        self._map_storage.get_coin_address_by_waves_address.assert_called_once_with(mock_waves_address)
        self.assertEqual(res, mock_coin_address)

    def test_create_address_invalid_waves_address(self):
        mock_waves_address = "72936587"
        mock_coin_address = "8120743689"

        self._waves_address_validation_service.validate_address.return_value = False
        self._map_storage.waves_address_exists.return_value = True
        self._map_storage.get_coin_address_by_waves_address.return_value = mock_coin_address

        with self.assertRaises(WavesAddressInvalidError):
            self._gateway_controller.create_address(mock_waves_address)

            self._waves_address_validation_service.assert_called_once_with(mock_waves_address)

    def test_create_address_not_exists_is_string(self):
        mock_waves_address = "72936587"
        mock_coin_address = "8120743689"
        expected_mapping = MappingEntry(coin_address=mock_coin_address, waves_address=mock_waves_address)

        self._waves_address_validation_service.validate_address.return_value = True
        self._map_storage.waves_address_exists.return_value = False
        self._coin_address_factory.create_address.return_value = mock_coin_address

        res = self._gateway_controller.create_address(mock_waves_address)

        self._map_storage.safely_save_mapping.assert_called_once_with(expected_mapping)
        self.assertEqual(res, mock_coin_address)

    def test_create_address_not_exists_is_key_pair(self):
        mock_waves_address = "72936587"
        mock_coin_address = "8120743689"
        mock_coin_secret = "2736984"
        mock_key_pair = KeyPair(public=mock_coin_address, secret=mock_coin_secret)
        expected_mapping = MappingEntry(coin_address=mock_coin_address, waves_address=mock_waves_address)

        self._waves_address_validation_service.validate_address.return_value = True
        self._map_storage.waves_address_exists.return_value = False
        self._coin_address_factory.create_address.return_value = mock_key_pair

        res = self._gateway_controller.create_address(mock_waves_address)

        self._wallet_storage.safely_save_address_secret.assert_called_once_with(mock_key_pair)
        self._map_storage.safely_save_mapping.assert_called_once_with(expected_mapping)
        self.assertEqual(res, mock_coin_address)

    def test_get_attempt_list_by_id(self):
        mock_find_by_attempt_list_id_result = MagicMock()
        mock_attempt_list_id = "27891623857"

        self._attempt_list_storage.find_by_attempt_list_id.return_value = mock_find_by_attempt_list_id_result
        res = self._gateway_controller.get_attempt_list_by_id(mock_attempt_list_id)
        self.assertEqual(res, mock_find_by_attempt_list_id_result)

    def test_query_attempt_lists(self):
        mock_query_attempt_lists_result = MagicMock()
        mock_attempt_list_query = AttemptListQuery(anything="7192835")

        self._attempt_list_storage.query_attempt_lists.return_value = mock_query_attempt_lists_result

        res = self._gateway_controller.query_attempt_lists(mock_attempt_list_query)

        self.assertEqual(res, mock_query_attempt_lists_result)
        self._attempt_list_storage.query_attempt_lists.assert_called_once_with(mock_attempt_list_query)

    def test_get_attempt_list_by_trigger(self):
        mock_find_by_trigger_result = MagicMock()
        mock_trigger = AttemptListTrigger(tx="2396487", receiver=3, currency="coin")
        self._attempt_list_storage.find_by_trigger.return_value = mock_find_by_trigger_result

        res = self._gateway_controller.get_attempt_list_by_trigger(mock_trigger)

        self.assertEqual(res, mock_find_by_trigger_result)
        self._attempt_list_storage.find_by_trigger.assert_called_once_with(mock_trigger)

    def test_check_coin_transaction_not_found(self):
        mock_tx = "867452378"
        self._coin_chain_query_service.get_transaction_by_tx.return_value = None

        with self.assertRaises(InvalidTransactionIdentifier):
            self._gateway_controller.check_coin_transaction(mock_tx)

        self._coin_chain_query_service.get_transaction_by_tx.assert_called_once_with(mock_tx)
        self._coin_transaction_consumer.handle_transaction.assert_not_called()

    def test_check_coin_transaction_found_but_not_relevant(self):
        mock_tx = "867452378"
        mock_transaction = MagicMock()
        self._coin_chain_query_service.get_transaction_by_tx.return_value = mock_transaction
        self._coin_transaction_consumer.filter_transaction.return_value = False

        self._gateway_controller.check_coin_transaction(mock_tx)

        self._coin_chain_query_service.get_transaction_by_tx.assert_called_once_with(mock_tx)
        self._coin_transaction_consumer.handle_transaction.assert_not_called()

    def test_check_coin_transaction_found(self):
        mock_tx = "867452378"
        mock_transaction = MagicMock()
        self._coin_chain_query_service.get_transaction_by_tx.return_value = mock_transaction
        self._coin_transaction_consumer.filter_transaction.return_value = True

        self._gateway_controller.check_coin_transaction(mock_tx)

        self._coin_chain_query_service.get_transaction_by_tx.assert_called_once_with(mock_tx)
        self._coin_transaction_consumer.handle_transaction.assert_called_once_with(mock_transaction)

    def test_check_waves_transaction_not_found(self):
        mock_tx = "867452378"
        self._waves_chain_query_service.get_transaction_by_tx.return_value = None

        with self.assertRaises(InvalidTransactionIdentifier):
            self._gateway_controller.check_waves_transaction(mock_tx)

        self._waves_chain_query_service.get_transaction_by_tx.assert_called_once_with(mock_tx)

    def test_check_waves_transaction_found_but_not_relevant(self):
        mock_tx = "867452378"
        mock_transaction = MagicMock()
        self._waves_chain_query_service.get_transaction_by_tx.return_value = mock_transaction
        self._waves_transaction_consumer.filter_transaction.return_value = False

        self._gateway_controller.check_waves_transaction(mock_tx)

        self._waves_chain_query_service.get_transaction_by_tx.assert_called_once_with(mock_tx)
        self._waves_transaction_consumer.handle_transaction.assert_not_called()

    def test_check_waves_transaction_found(self):
        mock_tx = "867452378"
        mock_transaction = MagicMock()
        self._waves_chain_query_service.get_transaction_by_tx.return_value = mock_transaction
        self._waves_transaction_consumer.filter_transaction.return_value = True

        self._gateway_controller.check_waves_transaction(mock_tx)

        self._waves_chain_query_service.get_transaction_by_tx.assert_called_once_with(mock_tx)
        self._waves_transaction_consumer.handle_transaction.assert_called_once_with(mock_transaction)
