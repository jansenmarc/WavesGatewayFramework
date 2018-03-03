"""
Transaction
"""

from typing import List, Union

from decimal import Decimal


class TransactionSender(object):
    """
    Stores information about the sender of an transaction.
    """
    DICT_ADDRESS_KEY = 'address'

    def __init__(self, address: str) -> None:
        self._address = address

    @property
    def address(self) -> str:
        return self._address

    def __eq__(self, other):
        if not isinstance(other, TransactionSender):
            return False
        else:
            res = True
            res = res and self._address == other.address
            return res


class TransactionReceiver(object):
    """
    Defines the amount which the transaction spends to a specific address.
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
        if not isinstance(other, TransactionReceiver):
            return False
        else:
            res = True
            res = res and self._address == other.address
            res = res and self._amount == other.amount
            return res


class Transaction(object):
    """
    Represents a transaction in any coin (including Waves).
    The sender may be any kind of public identifier that can be written as a string.
    In this package, this is the public part of some KeyPair derived class.
    """

    DICT_RECEIVERS_KEY = 'receivers'
    DICT_TX_KEY = 'tx'

    def __init__(self, tx: str, receivers: List[TransactionReceiver], senders: List[TransactionSender] = None) -> None:
        self._tx = tx
        self._receivers = receivers
        self._senders = senders

    @property
    def tx(self) -> str:
        return self._tx

    @property
    def receivers(self) -> List[TransactionReceiver]:
        return self._receivers

    @property
    def senders(self) -> List[TransactionSender]:
        return self._senders

    def __eq__(self, other):
        if not isinstance(other, Transaction):
            return False
        else:
            res = True
            res = res and self.receivers == other.receivers
            res = res and self.tx == other.tx
            # TODO: add senders here also???
            return res

    def __str__(self):
        return "Transaction(" + str(self.tx) + ")"
