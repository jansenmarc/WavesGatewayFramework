"""
AssetTransactionServiceConverterProxyImpl
"""

from typing import Optional, cast

from waves_gateway.common import Injectable
from waves_gateway.model import Transaction, TransactionAttempt
from waves_gateway.service.token import COIN_TRANSACTION_SERVICE, COIN_INTEGER_CONVERTER_SERVICE, \
    ASSET_INTEGER_CONVERTER_SERVICE

from .attempt_list_converter_service import AttemptListConverterService

from .transaction_service import TransactionService
from .integer_converter_service import IntegerConverterService
from .asset_transaction_service_impl import AssetTransactionServiceImpl
from .token import COIN_TRANSACTION_SERVICE_CONVERTER_PROXY, WAVES_TRANSACTION_SERVICE_CONVERTER_PROXY


@Injectable(
    COIN_TRANSACTION_SERVICE_CONVERTER_PROXY,
    deps=[COIN_INTEGER_CONVERTER_SERVICE, COIN_TRANSACTION_SERVICE, AttemptListConverterService])
@Injectable(
    WAVES_TRANSACTION_SERVICE_CONVERTER_PROXY,
    deps=[ASSET_INTEGER_CONVERTER_SERVICE, AssetTransactionServiceImpl, AttemptListConverterService])
class TransactionServiceConverterProxyImpl(TransactionService):
    """
    Reverts the amount conversion before overhanding the TransactionAttempt instance
    to the given TransactionService.
    """

    def __init__(self, integer_converter_service: IntegerConverterService, transaction_service: TransactionService,
                 attempt_list_converter_service: AttemptListConverterService) -> None:
        self._integer_converter_service = integer_converter_service
        self._transaction_service = transaction_service
        self._attempt_list_converter_service = attempt_list_converter_service

    def send_coin(self, attempt: TransactionAttempt, secret: Optional[str]) -> Transaction:
        converted_attempt = self._attempt_list_converter_service.revert_attempt_conversion(attempt)
        transaction = self._transaction_service.send_coin(converted_attempt, secret)
        return self._integer_converter_service.convert_transaction_to_int(transaction)
