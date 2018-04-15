"""
AttemptListConverterService
"""

from typing import cast

from waves_gateway.common import Injectable
from waves_gateway.model import TransactionAttempt, TransactionAttemptReceiver, TransactionAttemptList
from waves_gateway.service.token import COIN_INTEGER_CONVERTER_SERVICE, ASSET_INTEGER_CONVERTER_SERVICE

from .integer_converter_service import IntegerConverterService


@Injectable(deps=[COIN_INTEGER_CONVERTER_SERVICE, ASSET_INTEGER_CONVERTER_SERVICE])
class AttemptListConverterService(object):
    """
    Applies the particular converters on an TransactionAttemptList instance.
    """

    def __init__(self, coin_integer_converter_service: IntegerConverterService,
                 asset_integer_converter_service: IntegerConverterService) -> None:
        self._coin_integer_converter_service = coin_integer_converter_service
        self._asset_integer_converter_service = asset_integer_converter_service

    def revert_attempt_conversion(self, attempt: TransactionAttempt):
        if attempt.currency == "coin":
            cv = self._coin_integer_converter_service
        elif attempt.currency == "waves":
            cv = self._asset_integer_converter_service
        else:
            raise Exception("unknown currency")

        receivers = []

        for i in range(0, len(attempt.receivers)):
            amount = cast(int, attempt.receivers[i].amount)  # type: int

            receivers.append(
                TransactionAttemptReceiver(
                    amount=cv.revert_amount_conversion(amount), address=attempt.receivers[i].address))

        fee = attempt.fee

        if attempt.currency == "coin":
            fee = cv.revert_amount_conversion(cast(int, fee))

        return TransactionAttempt(receivers=receivers, fee=fee, sender=attempt.sender, currency=attempt.currency)

    def revert_attempt_list_conversion(self, attempt_list: TransactionAttemptList):
        converted_attempts = []

        for attempt in attempt_list.attempts:
            converted_attempts.append(self.revert_attempt_conversion(attempt))

        return TransactionAttemptList(
            attempts=converted_attempts,
            transactions=attempt_list.transactions,
            trigger=attempt_list.trigger,
            created_at=attempt_list.created_at,
            last_modified=attempt_list.last_modified,
            tries=attempt_list.tries,
            attempt_list_id=attempt_list.attempt_list_id)
