import pywaves  # type: ignore
from logging import Logger
from typing import cast
from unittest import TestCase
from unittest.mock import MagicMock, patch

from waves_gateway.model import Transaction, TransactionReceiver, KeyPair, TransactionAttemptList, TransactionAttempt, \
    TransactionAttemptReceiver, AttemptListTrigger
from waves_gateway.service import WavesTransactionConsumerImpl, \
    WavesChainQueryServiceImpl, FeeService, TransactionAttemptListService, AddressValidationService
from waves_gateway.storage import TransactionAttemptListStorage


class WavesTransactionConsumerImplTestMultiReceiver(TestCase):
    def setUp(self):
        self._coin_standard_fee = 7269
        self._gateway_waves_receiver = TransactionReceiver("9823748", 923235)
        self._gateway_waves_address_secret = KeyPair(public="9238746", secret="9236478")
        self._coin_transaction_service = MagicMock()
        self._waves_chain_query_service = MagicMock(spec=WavesChainQueryServiceImpl)
        self._waves_transaction_storage = MagicMock()
        self._logger = MagicMock()
        self._gateway_coin_address_secret = KeyPair(public="9374682o", secret="sdkjrlig")
        self._coin_transaction_storage = MagicMock()
        self._gateway_owner_coin_holder = "23u4oi362"
        self._gateway_fee = 8793
        self._gateway_owner_address = "923768"
        self._fee_service = MagicMock()
        self._only_one_transaction_receiver = False
        self._attempt_service = MagicMock()
        self._gateway_pywaves_address = MagicMock()
        self._gateway_pywaves_address.address = self._gateway_waves_receiver.address
        self._attempt_list_storage = MagicMock()
        self._coin_address_validation_service = MagicMock()

        self._waves_transaction_consumer_impl = WavesTransactionConsumerImpl(
            gateway_waves_address_secret=self._gateway_waves_address_secret,
            waves_chain_query_service=cast(WavesChainQueryServiceImpl, self._waves_chain_query_service),
            logger=cast(Logger, self._logger),
            gateway_owner_address=self._gateway_owner_address,
            gateway_coin_address_secret=self._gateway_coin_address_secret,
            fee_service=cast(FeeService, self._fee_service),
            only_one_transaction_receiver=cast(bool, self._only_one_transaction_receiver),
            attempt_service=cast(TransactionAttemptListService, self._attempt_service),
            gateway_pywaves_address=cast(pywaves.Address, self._gateway_pywaves_address),
            attempt_list_storage=cast(TransactionAttemptListStorage, self._attempt_list_storage),
            coin_address_validation_service=cast(AddressValidationService, self._coin_address_validation_service))

        self._fee_service.get_coin_fee.return_value = self._coin_standard_fee
        self._fee_service.get_gateway_fee.return_value = self._gateway_fee

    def test_filter_transaction_already_exists(self):
        """
        Should not pass a transaction that is existing in one of the attempt lists
        """
        transaction = Transaction(tx="78265", receivers=[TransactionReceiver('28734', 7823)])

        self._attempt_list_storage.gateway_transaction_exists.return_value = True
        res = self._waves_transaction_consumer_impl.filter_transaction(transaction)
        self.assertFalse(res)

    def test_filter_transaction_by_receiver_failure(self):
        """
        Should not pass a transaction with only one receiver which does not equal the gateway address
        """
        transaction = Transaction(tx="78265", receivers=[TransactionReceiver('28734', 7823)])
        self._attempt_list_storage.gateway_transaction_exists.return_value = False

        res = self._waves_transaction_consumer_impl.filter_transaction(transaction)
        self._attempt_list_storage.find_by_trigger.assert_not_called()
        self.assertFalse(res)

    def test_filter_transaction_by_receiver_success(self):
        """
        Should pass a transaction with a receiver that is addressed to the main
        gateway waves address
        """
        transaction = Transaction(tx="78265", receivers=[self._gateway_waves_receiver])
        self._attempt_list_storage.gateway_transaction_exists.return_value = False
        self._attempt_list_storage.find_by_trigger.return_value = None
        res = self._waves_transaction_consumer_impl.filter_transaction(transaction)
        self._attempt_list_storage.gateway_transaction_exists.assert_called_once_with(transaction.tx)
        self.assertTrue(res)

    def test_handle_transaction(self):
        _filter_receivers = MagicMock(return_value=[0])
        _handle_receiver = MagicMock()
        transaction = Transaction(tx="78265", receivers=[self._gateway_waves_receiver])

        with patch.multiple(
                self._waves_transaction_consumer_impl,
                _filter_receivers=_filter_receivers,
                _handle_receiver=_handle_receiver):
            self._waves_transaction_consumer_impl.handle_transaction(transaction)
            _filter_receivers.assert_called_once_with(transaction)
            _handle_receiver.assert_called_once_with(transaction.tx, self._gateway_waves_receiver, 0, None)

    @patch('datetime.datetime', autospec=True)
    def test_handle_receiver(self, mock_datetime: MagicMock):
        now = MagicMock()
        mock_datetime.utcnow.return_value = now

        coin_receiver = "82396457"
        amount_after_fees = self._gateway_waves_receiver.amount - self._coin_standard_fee - self._gateway_fee
        tx = "78265"
        self._coin_address_validation_service.validate_address.return_value = True

        attempts = [
            TransactionAttempt(
                sender=self._gateway_coin_address_secret.public,
                fee=self._coin_standard_fee,
                currency="coin",
                receivers=[
                    TransactionAttemptReceiver(address=coin_receiver, amount=amount_after_fees),
                    TransactionAttemptReceiver(address=self._gateway_owner_address, amount=self._gateway_fee)
                ])
        ]

        trigger = AttemptListTrigger(tx=tx, currency="waves", receiver=0)

        self._attempt_list_storage.find_by_trigger.return_value = None
        attempt_list = TransactionAttemptList(trigger=trigger, attempts=attempts, created_at=now, last_modified=now)

        self._waves_chain_query_service.get_coin_receiver_address_from_transaction.return_value = coin_receiver

        self._waves_transaction_consumer_impl._handle_receiver(tx, self._gateway_waves_receiver, 0)

        self._waves_chain_query_service.get_coin_receiver_address_from_transaction.assert_called_once_with(tx)
        self._attempt_service.continue_transaction_attempt_list.assert_not_called()
        self._attempt_list_storage.find_by_trigger.assert_called_once_with(
            AttemptListTrigger(tx=tx, currency="waves", receiver=0))
        self._attempt_list_storage.safely_save_attempt_list.assert_called_once_with(attempt_list)

    def test_handle_receiver_invalid_address(self):
        coin_receiver = "82396457"
        amount_after_fees = self._gateway_waves_receiver.amount - self._coin_standard_fee - self._gateway_fee
        tx = "78265"
        self._coin_address_validation_service.validate_address.return_value = False

        attempts = [
            TransactionAttempt(
                sender=self._gateway_coin_address_secret.public,
                fee=self._coin_standard_fee,
                currency="coin",
                receivers=[
                    TransactionAttemptReceiver(address=coin_receiver, amount=amount_after_fees),
                    TransactionAttemptReceiver(address=self._gateway_owner_address, amount=self._gateway_fee)
                ])
        ]

        trigger = AttemptListTrigger(tx=tx, currency="waves", receiver=0)

        self._attempt_list_storage.find_by_trigger.return_value = None

        self._waves_chain_query_service.get_coin_receiver_address_from_transaction.return_value = coin_receiver

        self._waves_transaction_consumer_impl._handle_receiver(tx, self._gateway_waves_receiver, 0)

        self._waves_chain_query_service.get_coin_receiver_address_from_transaction.assert_called_once_with(tx)
        self._coin_address_validation_service.validate_address.assert_called_once_with(coin_receiver)
        self._attempt_service.continue_transaction_attempt_list.assert_not_called()
        self._attempt_list_storage.find_by_trigger.assert_not_called()


class WavesTransactionConsumerImplTestSingleReceiver(TestCase):
    def setUp(self):
        self._coin_standard_fee = 7269
        self._gateway_waves_receiver = TransactionReceiver("9823748", 923235)
        self._gateway_waves_address_secret = KeyPair(public="9238746", secret="9236478")
        self._coin_transaction_service = MagicMock()
        self._waves_chain_query_service = MagicMock(spec=WavesChainQueryServiceImpl)
        self._waves_transaction_storage = MagicMock()
        self._logger = MagicMock()
        self._gateway_coin_address_secret = KeyPair(public="9374682o", secret="sdkjrlig")
        self._coin_transaction_storage = MagicMock()
        self._gateway_owner_coin_holder = "23u4oi362"
        self._gateway_fee = 8793
        self._gateway_owner_address = "923768"
        self._fee_service = MagicMock()
        self._only_one_transaction_receiver = True
        self._attempt_service = MagicMock()
        self._gateway_pywaves_address = MagicMock()
        self._gateway_pywaves_address.address = self._gateway_waves_receiver.address
        self._attempt_list_storage = MagicMock()
        self._coin_address_validation_service = MagicMock()

        self._waves_transaction_consumer_impl = WavesTransactionConsumerImpl(
            gateway_waves_address_secret=self._gateway_waves_address_secret,
            waves_chain_query_service=cast(WavesChainQueryServiceImpl, self._waves_chain_query_service),
            logger=cast(Logger, self._logger),
            gateway_owner_address=self._gateway_owner_address,
            gateway_coin_address_secret=self._gateway_coin_address_secret,
            fee_service=cast(FeeService, self._fee_service),
            only_one_transaction_receiver=cast(bool, self._only_one_transaction_receiver),
            attempt_service=cast(TransactionAttemptListService, self._attempt_service),
            gateway_pywaves_address=cast(pywaves.Address, self._gateway_pywaves_address),
            attempt_list_storage=cast(TransactionAttemptListStorage, self._attempt_list_storage),
            coin_address_validation_service=cast(AddressValidationService, self._coin_address_validation_service))

        self._fee_service.get_coin_fee.return_value = self._coin_standard_fee
        self._fee_service.get_gateway_fee.return_value = self._gateway_fee

    @patch('datetime.datetime', autospec=True)
    def test_handle_receiver(self, mock_datetime: MagicMock):
        now = MagicMock()
        mock_datetime.utcnow.return_value = now

        coin_receiver = "82396457"
        amount_after_fees = self._gateway_waves_receiver.amount - 2 * self._coin_standard_fee - self._gateway_fee
        tx = "78265"
        self._coin_address_validation_service.validate_address.return_value = True

        attempts = [
            TransactionAttempt(
                sender=self._gateway_coin_address_secret.public,
                fee=self._coin_standard_fee,
                currency="coin",
                receivers=[TransactionAttemptReceiver(address=coin_receiver, amount=amount_after_fees)]),
            TransactionAttempt(
                sender=self._gateway_coin_address_secret.public,
                fee=self._coin_standard_fee,
                currency="coin",
                receivers=[TransactionAttemptReceiver(address=self._gateway_owner_address, amount=self._gateway_fee)])
        ]

        trigger = AttemptListTrigger(tx=tx, currency="waves", receiver=0)

        self._attempt_list_storage.find_by_trigger.return_value = None
        attempt_list = TransactionAttemptList(trigger=trigger, attempts=attempts, created_at=now, last_modified=now)

        self._waves_chain_query_service.get_coin_receiver_address_from_transaction.return_value = coin_receiver

        self._waves_transaction_consumer_impl._handle_receiver(tx, self._gateway_waves_receiver, 0)

        self._waves_chain_query_service.get_coin_receiver_address_from_transaction.assert_called_once_with(tx)
        self._attempt_service.continue_transaction_attempt_list.assert_not_called()
        self._attempt_list_storage.find_by_trigger.assert_called_once_with(
            AttemptListTrigger(tx=tx, currency="waves", receiver=0))
        self._attempt_list_storage.safely_save_attempt_list.assert_called_once_with(attempt_list)


class WavesTransactionConsumerImplTestSingleReceiverNoGwFee(TestCase):
    def setUp(self):
        self._coin_standard_fee = 7269
        self._gateway_waves_receiver = TransactionReceiver("9823748", 923235)
        self._gateway_waves_address_secret = KeyPair(public="9238746", secret="9236478")
        self._coin_transaction_service = MagicMock()
        self._waves_chain_query_service = MagicMock(spec=WavesChainQueryServiceImpl)
        self._waves_transaction_storage = MagicMock()
        self._logger = MagicMock()
        self._gateway_coin_address_secret = KeyPair(public="9374682o", secret="sdkjrlig")
        self._coin_transaction_storage = MagicMock()
        self._gateway_owner_coin_holder = "23u4oi362"
        self._gateway_fee = 0
        self._gateway_owner_address = "923768"
        self._fee_service = MagicMock()
        self._only_one_transaction_receiver = True
        self._attempt_service = MagicMock()
        self._gateway_pywaves_address = MagicMock()
        self._gateway_pywaves_address.address = self._gateway_waves_receiver.address
        self._attempt_list_storage = MagicMock()
        self._coin_address_validation_service = MagicMock()

        self._waves_transaction_consumer_impl = WavesTransactionConsumerImpl(
            gateway_waves_address_secret=self._gateway_waves_address_secret,
            waves_chain_query_service=cast(WavesChainQueryServiceImpl, self._waves_chain_query_service),
            logger=cast(Logger, self._logger),
            gateway_owner_address=self._gateway_owner_address,
            gateway_coin_address_secret=self._gateway_coin_address_secret,
            fee_service=cast(FeeService, self._fee_service),
            only_one_transaction_receiver=cast(bool, self._only_one_transaction_receiver),
            attempt_service=cast(TransactionAttemptListService, self._attempt_service),
            gateway_pywaves_address=cast(pywaves.Address, self._gateway_pywaves_address),
            attempt_list_storage=cast(TransactionAttemptListStorage, self._attempt_list_storage),
            coin_address_validation_service=cast(AddressValidationService, self._coin_address_validation_service))

        self._fee_service.get_coin_fee.return_value = self._coin_standard_fee
        self._fee_service.get_gateway_fee.return_value = self._gateway_fee

    @patch('datetime.datetime', autospec=True)
    def test_handle_receiver(self, mock_datetime: MagicMock):
        now = MagicMock()
        mock_datetime.utcnow.return_value = now

        coin_receiver = "82396457"
        amount_after_fees = self._gateway_waves_receiver.amount - self._coin_standard_fee
        tx = "78265"
        self._coin_address_validation_service.validate_address.return_value = True

        attempts = [
            TransactionAttempt(
                sender=self._gateway_coin_address_secret.public,
                fee=self._coin_standard_fee,
                currency="coin",
                receivers=[TransactionAttemptReceiver(address=coin_receiver, amount=amount_after_fees)])
        ]

        trigger = AttemptListTrigger(tx=tx, currency="waves", receiver=0)

        self._attempt_list_storage.find_by_trigger.return_value = None
        attempt_list = TransactionAttemptList(trigger=trigger, attempts=attempts, created_at=now, last_modified=now)

        self._waves_chain_query_service.get_coin_receiver_address_from_transaction.return_value = coin_receiver

        self._waves_transaction_consumer_impl._handle_receiver(tx, self._gateway_waves_receiver, 0)

        self._waves_chain_query_service.get_coin_receiver_address_from_transaction.assert_called_once_with(tx)
        self._attempt_service.continue_transaction_attempt_list.assert_not_called()
        self._attempt_list_storage.find_by_trigger.assert_called_once_with(
            AttemptListTrigger(tx=tx, currency="waves", receiver=0))
        self._attempt_list_storage.safely_save_attempt_list.assert_called_once_with(attempt_list)
