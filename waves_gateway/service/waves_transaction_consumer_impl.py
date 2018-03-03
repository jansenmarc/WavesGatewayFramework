"""
WavesTransactionConsumerImpl
"""

from logging import Logger
from typing import List, cast

import datetime
import pywaves  # type: ignore

from waves_gateway.common import MultipleGatewayReceiversError, Injectable, GATEWAY_OWNER_ADDRESS, \
    GATEWAY_COIN_ADDRESS_SECRET, ONLY_ONE_TRANSACTION_RECEIVER, GATEWAY_WAVES_ADDRESS_SECRET, GATEWAY_PYWAVES_ADDRESS, \
    WAVES_CHAIN_QUERY_SERVICE_CONVERTER_PROXY
from waves_gateway.model import TransactionReceiver, \
    TransactionAttempt, TransactionAttemptReceiver, TransactionAttemptList, AttemptListTrigger, \
    Transaction, TransactionSender, KeyPair
from .fee_service_converter_proxy_impl import FeeServiceConverterProxyImpl

from .token import COIN_ADDRESS_VALIDATION_SERVICE
from waves_gateway.storage import TransactionAttemptListStorage

from .chain_query_service import ChainQueryService
from .address_validation_service import AddressValidationService
from .fee_service import FeeService
from .transaction_attempt_list_service import TransactionAttemptListService
from .transaction_consumer import TransactionConsumer


@Injectable(deps=[
    GATEWAY_WAVES_ADDRESS_SECRET, WAVES_CHAIN_QUERY_SERVICE_CONVERTER_PROXY, Logger, GATEWAY_OWNER_ADDRESS,
    GATEWAY_COIN_ADDRESS_SECRET, FeeServiceConverterProxyImpl, ONLY_ONE_TRANSACTION_RECEIVER,
    TransactionAttemptListService, GATEWAY_PYWAVES_ADDRESS, TransactionAttemptListStorage,
    COIN_ADDRESS_VALIDATION_SERVICE
])
class WavesTransactionConsumerImpl(TransactionConsumer):
    """
    Takes the received transactions from Waves and issues the resulting transactions
    in the custom cryptocurrency.
    """

    def __init__(self, gateway_waves_address_secret: KeyPair, waves_chain_query_service: ChainQueryService,
                 logger: Logger, gateway_owner_address: str, gateway_coin_address_secret: KeyPair,
                 fee_service: FeeService, only_one_transaction_receiver: bool,
                 attempt_service: TransactionAttemptListService, gateway_pywaves_address: pywaves.Address,
                 attempt_list_storage: TransactionAttemptListStorage,
                 coin_address_validation_service: AddressValidationService) -> None:
        self._gateway_waves_address_secret = gateway_waves_address_secret
        self._waves_chain_query_service = waves_chain_query_service
        self._logger = logger.getChild(self.__class__.__name__)
        self._gateway_owner_address = gateway_owner_address
        self._fee_service = fee_service
        self._gateway_coin_holder_secret = gateway_coin_address_secret
        self._only_one_transaction_receiver = only_one_transaction_receiver
        self._attempt_service = attempt_service
        self._gateway_pywaves_address = gateway_pywaves_address
        self._attempt_list_storage = attempt_list_storage
        self._coin_address_validation_service = coin_address_validation_service

    def filter_transaction(self, transaction: Transaction) -> bool:
        """
        Ensures that only transactions are handled that are
        addressed to the gateway main address.
        """
        if self._attempt_list_storage.gateway_transaction_exists(transaction.tx):
            return False
        else:
            return len(self._filter_receivers(transaction)) > 0

    def _filter_receivers(self, transaction: Transaction) -> List[int]:
        res = list()

        for i in range(0, len(transaction.receivers)):
            if self._gateway_pywaves_address.address == transaction.receivers[i].address:
                attempt_list = self._attempt_list_storage.find_by_trigger(
                    AttemptListTrigger(tx=transaction.tx, currency="waves", receiver=i))

                if attempt_list is None or not attempt_list.is_complete():
                    res.append(i)

        return res

    def _handle_receiver(self,
                         tx: str,
                         receiver: TransactionReceiver,
                         index: int,
                         senders: List[TransactionSender] = None) -> None:

        # ---------- Pre-Calculation ----------

        # fee to be used for the custom currency
        coin_fee = cast(int, self._fee_service.get_coin_fee())

        # fee to be transferred to the Gateway owner
        gateway_fee = cast(int, self._fee_service.get_gateway_fee())

        received_amount = cast(int, receiver.amount)

        # the amount of coins to be transferred after applying the fees
        if self._only_one_transaction_receiver:
            amount_after_fees = received_amount - 2 * coin_fee - gateway_fee
        else:
            amount_after_fees = received_amount - coin_fee - gateway_fee

        # receiver coin address
        coin_receiver = self._waves_chain_query_service.get_coin_receiver_address_from_transaction(tx)

        # ---------- Pre-Check ----------

        if not self._coin_address_validation_service.validate_address(coin_receiver):
            self._logger.warning("Received transaction %s with an invalid coin receiver address %s. "
                                 "Will be skipped.", tx, coin_receiver)
            return

        if self._gateway_coin_holder_secret.public == coin_receiver:
            self._logger.warning("Received transaction %s with the address of the Gateway coin holder."
                                 "Will be skipped as an transaction to itself has no effect.", tx)
            return

        # transaction must have at least a specific amount to be processed
        if amount_after_fees < 0:
            self._logger.warning("Received transaction %s with an amount of %s, but it is less than the at least "
                                 "required amount. Will be skipped.", tx, receiver.amount)
            return

        attempt_list = self._attempt_list_storage.find_by_trigger(
            AttemptListTrigger(tx=tx, currency="waves", receiver=index))

        if attempt_list is None:
            trigger = AttemptListTrigger(tx=tx, receiver=index, currency="waves", senders=senders)

            attempts = list()

            if self._only_one_transaction_receiver:
                attempts.append(
                    TransactionAttempt(
                        sender=self._gateway_coin_holder_secret.public,
                        fee=coin_fee,
                        currency="coin",
                        receivers=[TransactionAttemptReceiver(address=self._gateway_owner_address,
                                                              amount=gateway_fee)]))

                attempts.append(
                    TransactionAttempt(
                        sender=self._gateway_coin_holder_secret.public,
                        fee=coin_fee,
                        currency="coin",
                        receivers=[TransactionAttemptReceiver(address=coin_receiver, amount=amount_after_fees)]))
            else:
                attempts.append(
                    TransactionAttempt(
                        sender=self._gateway_coin_holder_secret.public,
                        fee=coin_fee,
                        currency="coin",
                        receivers=[
                            TransactionAttemptReceiver(address=coin_receiver, amount=amount_after_fees),
                            TransactionAttemptReceiver(address=self._gateway_owner_address, amount=gateway_fee)
                        ]))

            attempt_list = TransactionAttemptList(
                trigger, attempts, last_modified=datetime.datetime.utcnow(), created_at=datetime.datetime.utcnow())

            self._attempt_list_storage.safely_save_attempt_list(attempt_list)
            self._logger.info('Created new attempt list %s', str(attempt_list.attempt_list_id))

    def handle_transaction(self, transaction: Transaction) -> None:
        """
        Fetches the custom currency address which should be the receiver.
        Issues the transaction to the custom currency address.
        """

        receivers = self._filter_receivers(transaction)

        if len(receivers) > 1:
            raise MultipleGatewayReceiversError(transaction.tx)

        for i in receivers:
            self._handle_receiver(transaction.tx, transaction.receivers[i], i, transaction.senders)
