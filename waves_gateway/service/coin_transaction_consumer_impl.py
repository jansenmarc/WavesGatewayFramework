"""
CoinTransactionConsumerImpl
"""

from logging import Logger
from typing import List, cast

import datetime
import pywaves  # type: ignore

from waves_gateway.common import MappingNotFoundForCoinAddress, \
    MultipleGatewayReceiversError, Injectable, GATEWAY_OWNER_ADDRESS, GATEWAY_COIN_ADDRESS, \
    ONLY_ONE_TRANSACTION_RECEIVER, GATEWAY_WAVES_ADDRESS, GATEWAY_PYWAVES_ADDRESS
from waves_gateway.model import Transaction, TransactionReceiver, \
    TransactionAttempt, TransactionAttemptReceiver, TransactionAttemptList, \
    AttemptListTrigger, TransactionSender
from waves_gateway.storage import MapStorage, TransactionAttemptListStorage
from .fee_service import FeeService
from .transaction_attempt_list_service import TransactionAttemptListService
from .transaction_consumer import TransactionConsumer
from .fee_service_converter_proxy_impl import FeeServiceConverterProxyImpl


@Injectable(deps=[
    TransactionAttemptListService, GATEWAY_COIN_ADDRESS, MapStorage, Logger, GATEWAY_WAVES_ADDRESS,
    GATEWAY_OWNER_ADDRESS, FeeServiceConverterProxyImpl, ONLY_ONE_TRANSACTION_RECEIVER, GATEWAY_PYWAVES_ADDRESS,
    TransactionAttemptListStorage
])
class CoinTransactionConsumerImpl(TransactionConsumer):
    """
    Handles fetched transactions of the custom currency.
    """

    def __init__(self, attempt_service: TransactionAttemptListService, gateway_coin_address: str,
                 map_storage: MapStorage, logger: Logger, gateway_waves_address: str, gateway_owner_address: str,
                 fee_service: FeeService, only_one_transaction_receiver: bool, gateway_pywaves_address: pywaves.Address,
                 attempt_list_storage: TransactionAttemptListStorage) -> None:
        self._attempt_service = attempt_service
        self._gateway_coin_address = gateway_coin_address
        self._map_storage = map_storage
        self._logger = logger.getChild(self.__class__.__name__)
        self._gateway_waves_address = gateway_waves_address
        self._gateway_owner_address = gateway_owner_address
        self._fee_service = fee_service
        self._only_one_transaction_receiver = only_one_transaction_receiver
        self._gateway_pywaves_address = gateway_pywaves_address
        self._attempt_list_storage = attempt_list_storage

    def _is_gateway_managed_coin_address(self, address: str) -> bool:
        """
        Checks if there is a mapping entry belonging to the given address.
        """
        return self._map_storage.coin_address_exists(address)

    def _is_gateway_coin_holder(self, address: str):
        return address == self._gateway_coin_address

    def filter_transaction(self, transaction: Transaction) -> bool:
        """
        Returns whether the transaction is addressed to a gateway managed address.
        This is the case if at least one of the receivers is a gateway managed address.
        But, not the main gateway address.
        """
        if self._attempt_list_storage.gateway_transaction_exists(transaction.tx):
            return False
        else:
            return len(self._filter_receivers(transaction)) > 0

    def _filter_receivers(self, transaction: Transaction) -> List[int]:
        """
        Filters a given list of transaction receivers for those ones that are gateway managed, but not the
        main gateway coin holder. Those shall be further processed.
        """
        res = list()

        for i in range(0, len(transaction.receivers)):
            address = transaction.receivers[i].address

            if self._is_gateway_managed_coin_address(address) and not self._is_gateway_coin_holder(address):
                attempt_list = self._attempt_list_storage.find_by_trigger(
                    AttemptListTrigger(tx=transaction.tx, currency="coin", receiver=i))

                if attempt_list is None or not attempt_list.is_complete():
                    res.append(i)

        return res

    def _handle_transaction_receiver(self,
                                     tx: str,
                                     receiver: TransactionReceiver,
                                     index: int,
                                     senders: List[TransactionSender] = None):

        # ---------- Pre-Calculation ----------

        # the gateway address that coins were transferred to
        gateway_managed_address = receiver.address

        # the custom currency fee to be used
        coin_fee = cast(int, self._fee_service.get_coin_fee())

        # the waves fee to be used; not used in the calculation
        waves_fee = cast(int, self._fee_service.get_waves_fee())

        # the fee for the gateway owner; service costs
        gateway_fee = cast(int, self._fee_service.get_gateway_fee())

        # the amount of coins that were received by this receiver
        received_amount = cast(int, receiver.amount)

        # the waves address to receive the amount of coins
        receiver_waves_address = self._map_storage.get_waves_address_by_coin_address(gateway_managed_address)

        # the amount of coins to be transferred after applying the fees
        if self._only_one_transaction_receiver:
            amount_after_fees = received_amount - 2 * coin_fee - gateway_fee
        else:
            amount_after_fees = received_amount - coin_fee - gateway_fee

        # ---------- Pre-Check ----------

        # transaction must have minimum amount to be handled
        if amount_after_fees <= 0:
            self._logger.warn("Received transaction %s with an amount of %s, but it is less than the at least "
                              "required amount. Will be skipped, but marked as processed.", tx, receiver.amount)
            return

        # no mapping was found for some reason; this in an internal error as this should
        # already be prevented by the filter method
        if receiver_waves_address is None:
            raise MappingNotFoundForCoinAddress(gateway_managed_address)

        attempt_list = self._attempt_list_storage.find_by_trigger(
            AttemptListTrigger(tx=tx, currency="coin", receiver=index))

        if attempt_list is None:

            attempts = list()

            if self._only_one_transaction_receiver:
                attempts.append(
                    TransactionAttempt(
                        sender=gateway_managed_address,
                        currency="coin",
                        fee=coin_fee,
                        receivers=[
                            TransactionAttemptReceiver(address=self._gateway_coin_address, amount=amount_after_fees),
                        ]))

                attempts.append(
                    TransactionAttempt(
                        sender=gateway_managed_address,
                        currency="coin",
                        fee=coin_fee,
                        receivers=[TransactionAttemptReceiver(address=self._gateway_owner_address,
                                                              amount=gateway_fee)]))
            else:
                attempts.append(
                    TransactionAttempt(
                        sender=gateway_managed_address,
                        currency="coin",
                        fee=coin_fee,
                        receivers=[
                            TransactionAttemptReceiver(address=self._gateway_coin_address, amount=amount_after_fees),
                            TransactionAttemptReceiver(address=self._gateway_owner_address, amount=gateway_fee)
                        ]))

            attempts.append(
                TransactionAttempt(
                    sender=self._gateway_pywaves_address.address,
                    fee=waves_fee,
                    currency="waves",
                    receivers=[TransactionAttemptReceiver(address=receiver_waves_address, amount=amount_after_fees)]))

            trigger = AttemptListTrigger(tx, index, "coin", senders=senders)
            attempt_list = TransactionAttemptList(
                trigger, attempts, last_modified=datetime.datetime.utcnow(), created_at=datetime.datetime.utcnow())
            self._attempt_list_storage.safely_save_attempt_list(attempt_list)
            self._logger.info('Created new attempt list %s', str(attempt_list.attempt_list_id))

    def handle_transaction(self, transaction: Transaction) -> None:
        """
        Processes an incoming transaction in the custom currency.

        First, it fetches the current amount of coins stored on the gateway managed address which should
        already include what has been transferred.
        The amount of coins of the transaction must be determined.

        The further processing depends on whether this is a account based system.
        If not, an internal transaction is done, transferring the received amount to the
        main gateway address.
        Otherwise, the internal transaction is skipped.

        Finally, the waves transaction is performed.
        """
        receivers = self._filter_receivers(transaction)

        if len(receivers) > 1:
            raise MultipleGatewayReceiversError(transaction.tx)

        for i in receivers:
            self._handle_transaction_receiver(transaction.tx, transaction.receivers[i], i, transaction.senders)
