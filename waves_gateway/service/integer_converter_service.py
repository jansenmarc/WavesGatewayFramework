"""
IntegerConverterService
"""

from abc import ABC
from typing import Union, cast
from copy import deepcopy

from decimal import Decimal

from waves_gateway.model import Transaction, TransactionReceiver


class IntegerConverterService(ABC):
    """
    Defines the requires functionality for an IntegerConverterService.
    It must allow the conversion from a float value to an int value and backwards.
    By default, it does not perform any conversion.
    """

    # noinspection PyMethodMayBeStatic
    def revert_amount_conversion(self, amount: int) -> Union[int, Decimal]:
        """Returns the argument by default (if not overwritten)."""
        return amount

    # noinspection PyMethodMayBeStatic
    def convert_amount_to_int(self, amount: Union[int, Decimal]) -> int:
        """Returns the argument by default (if not overwritten)."""
        return cast(int, amount)

    def safely_convert_to_int(self, amount: Union[int, Decimal]) -> int:
        """
        Tests the result of convert_amount_to_int if it has the type int.
        If not, it raises an TypeError.
        """
        converted = self.convert_amount_to_int(amount)

        if isinstance(converted, int):
            return converted
        else:
            raise TypeError('value must be an integer; value was ' + str(converted))

    def convert_transaction_to_int(self, transaction: Transaction) -> Transaction:
        res = deepcopy(transaction)

        for i in range(0, len(res.receivers)):
            receiver = res.receivers[i]
            res.receivers[i] = TransactionReceiver(receiver.address, self.safely_convert_to_int(receiver.amount))

        return res

    def revert_transaction_conversion(self, transaction: Transaction) -> Transaction:
        res = deepcopy(transaction)

        for i in range(0, len(res.receivers)):
            receiver = res.receivers[i]
            res.receivers[i] = TransactionReceiver(receiver.address,
                                                   self.revert_amount_conversion(cast(int, receiver.amount)))

        return res
