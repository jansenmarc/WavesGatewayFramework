"""
FailedTransaction
"""
import datetime
from uuid import uuid4
from typing import Optional


class FailedTransaction(object):
    """
    Model for failed tx
    """
    DICT_ID = "failed_transaction_id"
    DICT_CURRENCY = "currency"
    DICT_CAUSE = "reason"
    DICT_MESSAGE = "message"
    DICT_DATE = "date"
    DICT_TRANSACTION = "transaction"
    DICT_BACK_TRANSFER_ATTEMPTLIST = "back_transfer_attemptlist"

    def __init__(self, id: Optional[str], currency: str, cause: str, message: str, date, transaction: dict,
                 back_transfer_attemptlist: Optional[str]) -> None:
        self.cause = cause
        self._currency = currency
        self._message = message
        self._date = date
        self._transaction = transaction
        self._back_transfer_attemptlist = back_transfer_attemptlist

        if id is None or "":
            self._id = str(uuid4())
        else:
            self._id = id

    @property
    def id(self):
        return self._id

    @property
    def currency(self):
        return self._currency

    @property
    def name(self):
        return self.cause

    @property
    def message(self):
        return self._message

    @property
    def date(self):
        return self._date

    @property
    def transaction(self):
        return self._transaction

    @property
    def back_transfer_attemptlist(self):
        return self._back_transfer_attemptlist

    def set_back_transfer_attemptlist(self, id):
        self._back_transfer_attemptlist = id
