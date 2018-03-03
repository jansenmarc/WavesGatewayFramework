"""
TransactionAttemptList
"""

from typing import List, Optional
from uuid import uuid4

import datetime

from .transaction_attempt import TransactionAttempt
from .transaction import TransactionSender


class AttemptListTrigger(object):
    """
    Represents the receiver index of the transaction that has triggered the creation of an
    particular TransactionAttemptList instance.
    """
    DICT_TX = "tx"
    DICT_RECEIVER = "receiver"
    DICT_CURRENCY = "currency"
    DICT_SENDERS_KEY = 'senders'

    def __init__(self, tx: str, receiver: int, currency: str, senders: List[TransactionSender] = None) -> None:
        self._tx = tx
        self._receiver = receiver
        self._currency = currency
        self._senders = senders

    @property
    def tx(self):
        return self._tx

    @property
    def receiver(self):
        return self._receiver

    @property
    def currency(self):
        return self._currency

    @property
    def senders(self):
        return self._senders

    def __eq__(self, other):
        return self.tx == other.tx and self.receiver == other.receiver and self.currency == other.currency


class TransactionAttemptList(object):
    """
    Stores a list of attempts and their corresponding transactions if any.
    An TransactionAttemptList instance defines the progress of processing an incoming transaction.
    The incoming transaction itself is stored as the trigger of the TransactionAttemptList.
    Attempts represent the transactions that are meant to follow the trigger, but they may not already be processed.
    This is expressed by the transactions array in so far that if the transactions array has the same length
    as the attempts array, this means that all attempts have been processed.
    So, each entry in the transactions array is the transaction id of the corresponding TransactionAttempt.
    """
    DICT_ID = "attempt_list_id"
    DICT_TRANSACTIONS = "transactions"
    DICT_ATTEMPTS = "attempts"
    DICT_TRIGGER = "trigger"
    DICT_LAST_MODIFIED = "last_modified"
    DICT_CREATED_AT = "created_at"
    DICT_TRIES = "tries"
    DEFAULT_TRIES = 0

    def __init__(self,
                 trigger: AttemptListTrigger,
                 attempts: List[TransactionAttempt],
                 transactions: Optional[List] = None,
                 created_at: Optional[datetime.datetime] = None,
                 last_modified: Optional[datetime.datetime] = None,
                 tries: int = DEFAULT_TRIES,
                 attempt_list_id: Optional[str] = None) -> None:
        self._trigger = trigger
        self._attempts = attempts
        self._tries = tries
        self._created_at = created_at
        self._last_modified = last_modified

        if transactions is None:
            self._transactions = list()  # type: List[str]
        else:
            self._transactions = transactions

        if attempt_list_id is None:
            self._attempt_list_id = str(uuid4())
        else:
            self._attempt_list_id = attempt_list_id

    @property
    def attempt_list_id(self):
        return self._attempt_list_id

    @property
    def transactions(self) -> List[str]:
        return self._transactions

    @property
    def attempts(self) -> List[TransactionAttempt]:
        return self._attempts

    @property
    def trigger(self):
        return self._trigger

    @property
    def last_modified(self) -> Optional[datetime.datetime]:
        return self._last_modified

    @property
    def created_at(self) -> Optional[datetime.datetime]:
        return self._created_at

    @property
    def tries(self) -> int:
        return self._tries

    def mark_next_attempt_as_complete(self, attempt: TransactionAttempt, tx: str) -> None:
        for i in range(0, len(self._attempts)):
            if self._attempts[i] is attempt:
                if len(self._transactions) != i:
                    raise Exception("Trying to mark an attempt as complete that is not the next attempt")
                self._transactions.append(tx)
                self._last_modified = datetime.datetime.utcnow()

    def increment_tries(self):
        self._tries = self._tries + 1
        self._last_modified = datetime.datetime.utcnow()

    def next_incomplete_attempt(self) -> TransactionAttempt:
        return self._attempts[len(self._transactions)]

    def is_complete(self):
        return len(self._transactions) >= len(self._attempts)

    def __eq__(self, other):
        return self.created_at == other.created_at and self.last_modified == other.last_modified and self.transactions == other.transactions and self.attempts == other.attempts and self.trigger == other.trigger
