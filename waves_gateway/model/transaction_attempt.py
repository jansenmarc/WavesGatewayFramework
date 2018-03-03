"""
TransactionAttempt
"""

from typing import List, Union

from decimal import Decimal


class TransactionAttemptReceiver(object):
    """
    Defines the amount that shall be transferred to a specific receiver address.
    """
    DICT_ADDRESS_KEY = 'address'
    DICT_AMOUNT_KEY = 'amount'

    def __init__(self, address: str, amount: Union[int, Decimal]) -> None:
        self._address = address
        self._amount = amount

    @property
    def address(self) -> str:
        return self._address

    @property
    def amount(self) -> Union[int, Decimal]:
        return self._amount

    def __eq__(self, other):
        if not isinstance(other, TransactionAttemptReceiver):
            return False
        else:
            res = True
            res = res and self._address == other.address
            res = res and self._amount == other.amount
            return res


class TransactionAttempt(object):
    """
    An TransactionAttempt defines a planned transaction. This is a transaction
    that may not have been performed, yet. But is meant to be performed in the future.
    """
    DICT_FEE = "fee"
    DICT_SENDER = "sender"
    DICT_RECEIVERS = "receivers"
    DICT_CURRENCY = "currency"

    def __init__(
            self,
            sender: str,
            receivers: List[TransactionAttemptReceiver],
            fee: Union[int, Decimal],
            currency: str,
    ) -> None:
        self._sender = sender
        self._receivers = receivers
        self._fee = fee
        self._currency = currency

    @property
    def fee(self) -> Union[int, Decimal]:
        return self._fee

    @property
    def sender(self) -> str:
        return self._sender

    @property
    def receivers(self) -> List[TransactionAttemptReceiver]:
        return self._receivers

    @property
    def currency(self) -> str:
        return self._currency

    def overall_amount(self) -> Union[int, Decimal]:
        amount = 0

        for receiver in self._receivers:
            amount = amount + receiver.amount  # type: ignore

        return amount

    def __eq__(self, other):
        res = True
        res = res and self.receivers == other.receivers
        res = res and self.sender == other.sender
        res = res and self.fee == other.fee
        res = res and self.currency == other.currency

        return res
