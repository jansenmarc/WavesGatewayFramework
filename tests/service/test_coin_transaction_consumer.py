import pywaves  # type: ignore
import datetime
from logging import Logger
from typing import cast
from unittest import TestCase
from unittest.mock import MagicMock, patch

from waves_gateway.model import Transaction, TransactionReceiver, TransactionAttemptList, TransactionAttempt, \
    TransactionAttemptReceiver, AttemptListTrigger
from waves_gateway.service import CoinTransactionConsumerImpl, \
    ChainQueryService, TransactionAttemptListService, FeeService
from waves_gateway.storage import WalletStorage, MapStorage, TransactionAttemptListStorage


class CoinTransactionConsumerImplTestMultiReceiver(TestCase):
    """Should create attempt lists with multiple receivers."""

    def setUp(self):
        self._waves_standard_fee = 10000
        self._coin_standard_fee = 10111
        self._gateway_managed_receiver = TransactionReceiver('826323', 7710475)
        self._not_gateway_managed_receiver = TransactionReceiver('871263', 9992323)
        self._wallet_storage = MagicMock(spec=WalletStorage)
        self._coin_chain_query_service = MagicMock(spec=ChainQueryService)
        self._gateway_address = '7625897'
        self._gateway_coin_holder_receiver = TransactionReceiver(self._gateway_address, 6758)
        self._map_storage = MagicMock()
        self._logger = MagicMock()
        self._waves_transaction_storage = MagicMock()
        self._gateway_waves_address = "jshdj"
        self._gateway_owner_address = '263587234'
        self._attempt_service = MagicMock()
        self._fee_service = MagicMock()
        self._gateway_fee = 2344
        self._gateway_pywaves_address = MagicMock()
        self._gateway_pywaves_address.address = self._gateway_waves_address
        self._attempt_list_storage = MagicMock()

        self._coin_transaction_consumer_impl = CoinTransactionConsumerImpl(
            attempt_service=cast(TransactionAttemptListService, self._attempt_service),
            gateway_coin_address=self._gateway_address,
            map_storage=cast(MapStorage, self._map_storage),
            logger=cast(Logger, self._logger),
            gateway_waves_address=self._gateway_waves_address,
            gateway_owner_address=self._gateway_owner_address,
            fee_service=cast(FeeService, self._fee_service),
            only_one_transaction_receiver=False,
            gateway_pywaves_address=cast(pywaves.Address, self._gateway_pywaves_address),
            attempt_list_storage=cast(TransactionAttemptListStorage, self._attempt_list_storage))

        self._fee_service.get_coin_fee.return_value = self._coin_standard_fee
        self._fee_service.get_gateway_fee.return_value = self._gateway_fee
        self._fee_service.get_waves_fee.return_value = self._waves_standard_fee

    def test_filter_transaction_exists(self):
        """
        The filter should not allow transactions to pass which were already processed
        """

        with patch.object(self._coin_transaction_consumer_impl, "_filter_receivers"):
            self._attempt_service.gateway_transaction_exists.return_value = True
            transaction = Transaction(tx='723968', receivers=[self._gateway_managed_receiver])
            res = self._coin_transaction_consumer_impl.filter_transaction(transaction)
            self.assertFalse(res)
            cast(MagicMock, self._coin_transaction_consumer_impl._filter_receivers).assert_not_called()

    def test_filter_transaction_by_receivers_success(self):
        """
        The filter should pass a transaction that has not yet been processed and
        contains a gateway managed address
        """
        self._attempt_list_storage.gateway_transaction_exists.return_value = False
        self._map_storage.coin_address_exists.return_value = True
        self._attempt_list_storage.find_by_trigger.return_value = None
        transaction = Transaction(tx='723968', receivers=[self._gateway_managed_receiver])
        res = self._coin_transaction_consumer_impl.filter_transaction(transaction)
        self.assertTrue(res)
        self._map_storage.coin_address_exists.assert_called_once_with(self._gateway_managed_receiver.address)
        self._attempt_list_storage.find_by_trigger.assert_called_once_with(
            AttemptListTrigger(tx=transaction.tx, receiver=0, currency="coin"))

    def test_filter_transaction_by_receivers_failure(self):
        """
        The filter should ignore transactions with no gateway managed receivers
        """
        self._attempt_list_storage.gateway_transaction_exists.return_value = False
        self._map_storage.coin_address_exists.return_value = False
        transaction = Transaction(tx='723968', receivers=[self._not_gateway_managed_receiver])
        res = self._coin_transaction_consumer_impl.filter_transaction(transaction)
        self.assertFalse(res)
        self._map_storage.coin_address_exists.assert_called_once_with(self._not_gateway_managed_receiver.address)
        self._attempt_list_storage.find_by_trigger.assert_not_called()

    def test_filter_transaction_block_coin_holder(self):
        """
        The filter should not allow transactions that are addressed to the gateway coin holder
        """
        self._attempt_list_storage.gateway_transaction_exists.return_value = False
        self._map_storage.coin_address_exists.return_value = True
        transaction = Transaction(tx='723968', receivers=[self._gateway_coin_holder_receiver])
        res = self._coin_transaction_consumer_impl.filter_transaction(transaction)
        self.assertFalse(res)
        self._map_storage.coin_address_exists.assert_called_once_with(self._gateway_coin_holder_receiver.address)
        self._attempt_list_storage.gateway_transaction_exists.assert_called_once_with(transaction.tx)

    @patch('datetime.datetime', autospec=True)
    def test_handle_transaction_multi_receiver(self, mock_datetime: MagicMock):
        now = MagicMock()
        mock_datetime.utcnow.return_value = now
        gateway_coin_address = self._gateway_managed_receiver.address
        dst_waves_address = '039769'
        incoming_transaction = Transaction(tx='723968', receivers=[self._gateway_managed_receiver])

        amount_after_fees = self._gateway_managed_receiver.amount - self._coin_standard_fee - self._gateway_fee

        attempts = [
            TransactionAttempt(
                sender=gateway_coin_address,
                currency="coin",
                fee=self._coin_standard_fee,
                receivers=[
                    TransactionAttemptReceiver(address=self._gateway_address, amount=amount_after_fees),
                    TransactionAttemptReceiver(address=self._gateway_owner_address, amount=self._gateway_fee)
                ]),
            TransactionAttempt(
                sender=self._gateway_waves_address,
                fee=self._waves_standard_fee,
                currency="waves",
                receivers=[TransactionAttemptReceiver(address=dst_waves_address, amount=amount_after_fees)])
        ]

        trigger = AttemptListTrigger(tx=incoming_transaction.tx, currency="coin", receiver=0)

        attempt_list = TransactionAttemptList(trigger=trigger, attempts=attempts, created_at=now, last_modified=now)

        self._attempt_list_storage.find_by_trigger.return_value = None
        self._map_storage.get_waves_address_by_coin_address.return_value = dst_waves_address

        self._coin_transaction_consumer_impl.handle_transaction(incoming_transaction)

        self._attempt_list_storage.find_by_trigger.assert_any_call(
            AttemptListTrigger(tx=incoming_transaction.tx, receiver=0, currency="coin"))
        self._map_storage.get_waves_address_by_coin_address.assert_called_once_with(gateway_coin_address)
        self._attempt_service.continue_transaction_attempt_list.assert_not_called()
        self._attempt_list_storage.safely_save_attempt_list.assert_called_once_with(attempt_list)


class CoinTransactionConsumerImplTestSingleReceiver(TestCase):
    def setUp(self):
        self._waves_standard_fee = 10000
        self._coin_standard_fee = 10111
        self._gateway_managed_receiver = TransactionReceiver('826323', 7710475)
        self._not_gateway_managed_receiver = TransactionReceiver('871263', 9992323)
        self._wallet_storage = MagicMock(spec=WalletStorage)
        self._coin_chain_query_service = MagicMock(spec=ChainQueryService)
        self._gateway_address = '7625897'
        self._gateway_coin_holder_receiver = TransactionReceiver(self._gateway_address, 6758)
        self._map_storage = MagicMock()
        self._logger = MagicMock()
        self._waves_transaction_storage = MagicMock()
        self._gateway_waves_address = "jshdj"
        self._gateway_owner_address = '263587234'
        self._attempt_service = MagicMock()
        self._fee_service = MagicMock()
        self._gateway_fee = 2344
        self._gateway_pywaves_address = MagicMock()
        self._gateway_pywaves_address.address = self._gateway_waves_address
        self._attempt_list_storage = MagicMock()

        self._coin_transaction_consumer_impl = CoinTransactionConsumerImpl(
            attempt_service=cast(TransactionAttemptListService, self._attempt_service),
            gateway_coin_address=self._gateway_address,
            map_storage=cast(MapStorage, self._map_storage),
            logger=cast(Logger, self._logger),
            gateway_waves_address=self._gateway_waves_address,
            gateway_owner_address=self._gateway_owner_address,
            fee_service=cast(FeeService, self._fee_service),
            only_one_transaction_receiver=True,
            gateway_pywaves_address=cast(pywaves.Address, self._gateway_pywaves_address),
            attempt_list_storage=cast(TransactionAttemptListStorage, self._attempt_list_storage))

        self._fee_service.get_coin_fee.return_value = self._coin_standard_fee
        self._fee_service.get_gateway_fee.return_value = self._gateway_fee
        self._fee_service.get_waves_fee.return_value = self._waves_standard_fee

    @patch('datetime.datetime', autospec=True)
    def test_handle_transaction_only_one_receiver(self, mock_datetime: MagicMock):
        now = MagicMock()
        mock_datetime.utcnow.return_value = now
        gateway_coin_address = self._gateway_managed_receiver.address
        dst_waves_address = '039769'
        incoming_transaction = Transaction(tx='723968', receivers=[self._gateway_managed_receiver])

        amount_after_fees = self._gateway_managed_receiver.amount - 2 * self._coin_standard_fee - self._gateway_fee

        attempts = [
            TransactionAttempt(
                sender=gateway_coin_address,
                currency="coin",
                fee=self._coin_standard_fee,
                receivers=[TransactionAttemptReceiver(address=self._gateway_address, amount=amount_after_fees)]),
            TransactionAttempt(
                sender=gateway_coin_address,
                currency="coin",
                fee=self._coin_standard_fee,
                receivers=[TransactionAttemptReceiver(address=self._gateway_owner_address, amount=self._gateway_fee)]),
            TransactionAttempt(
                sender=self._gateway_waves_address,
                fee=self._waves_standard_fee,
                currency="waves",
                receivers=[TransactionAttemptReceiver(address=dst_waves_address, amount=amount_after_fees)])
        ]

        trigger = AttemptListTrigger(tx=incoming_transaction.tx, currency="coin", receiver=0)

        attempt_list = TransactionAttemptList(trigger=trigger, attempts=attempts, created_at=now, last_modified=now)

        self._attempt_list_storage.find_by_trigger.return_value = None
        self._map_storage.get_waves_address_by_coin_address.return_value = dst_waves_address

        self._coin_transaction_consumer_impl.handle_transaction(incoming_transaction)

        self._attempt_list_storage.find_by_trigger.assert_any_call(
            AttemptListTrigger(tx=incoming_transaction.tx, receiver=0, currency="coin"))
        self._map_storage.get_waves_address_by_coin_address.assert_called_once_with(gateway_coin_address)
        self._attempt_service.continue_transaction_attempt_list.assert_not_called()
        self._attempt_list_storage.safely_save_attempt_list.assert_called_once_with(attempt_list)


class CoinTransactionConsumerImplTestSingleReceiverNoGwFee(TestCase):
    def setUp(self):
        self._waves_standard_fee = 10000
        self._coin_standard_fee = 10111
        self._gateway_managed_receiver = TransactionReceiver('826323', 7710475)
        self._not_gateway_managed_receiver = TransactionReceiver('871263', 9992323)
        self._wallet_storage = MagicMock(spec=WalletStorage)
        self._coin_chain_query_service = MagicMock(spec=ChainQueryService)
        self._gateway_address = '7625897'
        self._gateway_coin_holder_receiver = TransactionReceiver(self._gateway_address, 6758)
        self._map_storage = MagicMock()
        self._logger = MagicMock()
        self._waves_transaction_storage = MagicMock()
        self._gateway_waves_address = "jshdj"
        self._gateway_owner_address = '263587234'
        self._attempt_service = MagicMock()
        self._fee_service = MagicMock()
        self._gateway_fee = 0
        self._gateway_pywaves_address = MagicMock()
        self._gateway_pywaves_address.address = self._gateway_waves_address
        self._attempt_list_storage = MagicMock()

        self._coin_transaction_consumer_impl = CoinTransactionConsumerImpl(
            attempt_service=cast(TransactionAttemptListService, self._attempt_service),
            gateway_coin_address=self._gateway_address,
            map_storage=cast(MapStorage, self._map_storage),
            logger=cast(Logger, self._logger),
            gateway_waves_address=self._gateway_waves_address,
            gateway_owner_address=self._gateway_owner_address,
            fee_service=cast(FeeService, self._fee_service),
            only_one_transaction_receiver=True,
            gateway_pywaves_address=cast(pywaves.Address, self._gateway_pywaves_address),
            attempt_list_storage=cast(TransactionAttemptListStorage, self._attempt_list_storage))

        self._fee_service.get_coin_fee.return_value = self._coin_standard_fee
        self._fee_service.get_gateway_fee.return_value = self._gateway_fee
        self._fee_service.get_waves_fee.return_value = self._waves_standard_fee

    @patch('datetime.datetime', autospec=True)
    def test_handle_transaction_only_one_receiver(self, mock_datetime: MagicMock):
        now = MagicMock()
        mock_datetime.utcnow.return_value = now
        gateway_coin_address = self._gateway_managed_receiver.address
        dst_waves_address = '039769'
        incoming_transaction = Transaction(tx='723968', receivers=[self._gateway_managed_receiver])

        amount_after_fees = self._gateway_managed_receiver.amount - self._coin_standard_fee

        attempts = [
            TransactionAttempt(
                sender=gateway_coin_address,
                currency="coin",
                fee=self._coin_standard_fee,
                receivers=[TransactionAttemptReceiver(address=self._gateway_address, amount=amount_after_fees)]),
            TransactionAttempt(
                sender=self._gateway_waves_address,
                fee=self._waves_standard_fee,
                currency="waves",
                receivers=[TransactionAttemptReceiver(address=dst_waves_address, amount=amount_after_fees)])
        ]

        trigger = AttemptListTrigger(tx=incoming_transaction.tx, currency="coin", receiver=0)

        attempt_list = TransactionAttemptList(trigger=trigger, attempts=attempts, created_at=now, last_modified=now)

        self._attempt_list_storage.find_by_trigger.return_value = None
        self._map_storage.get_waves_address_by_coin_address.return_value = dst_waves_address

        self._coin_transaction_consumer_impl.handle_transaction(incoming_transaction)

        self._attempt_list_storage.find_by_trigger.assert_any_call(
            AttemptListTrigger(tx=incoming_transaction.tx, receiver=0, currency="coin"))
        self._map_storage.get_waves_address_by_coin_address.assert_called_once_with(gateway_coin_address)
        self._attempt_service.continue_transaction_attempt_list.assert_not_called()
        self._attempt_list_storage.safely_save_attempt_list.assert_called_once_with(attempt_list)
