"""
FailedTransaction
"""
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

    def __init__(self,
                 currency: str,
                 cause: str,
                 message: str,
                 date,
                 transaction: dict,
                 back_transfer_attemptlist: Optional[str] = None,
                 id: Optional[str] = None) -> None:
        self._cause = cause
        self._currency = currency
        self._message = message
        self._date = date
        self._transaction = transaction
        self._back_transfer_attemptlist = back_transfer_attemptlist

        if id is None:
            self._id = str(uuid4())
        else:
            self._id = id

    @property
    def id(self) -> Optional[str]:
        return self._id

    @property
    def currency(self) -> str:
        return self._currency

    @property
    def cause(self) -> str:
        return self._cause

    @property
    def message(self) -> str:
        return self._message

    @property
    def date(self):
        return self._date

    @property
    def transaction(self) -> dict:
        return self._transaction

    @property
    def back_transfer_attemptlist(self) -> Optional[str]:
        return self._back_transfer_attemptlist

    @back_transfer_attemptlist.setter
    def back_transfer_attemptlist(self, id):
        self._back_transfer_attemptlist = id

    @cause.setter
    def cause(self, cause: str):
        self._cause = cause
