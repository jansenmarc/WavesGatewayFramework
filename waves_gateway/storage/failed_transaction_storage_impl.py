"""
FailedTransactionStorageImpl
"""
from waves_gateway.common import Injectable, GATEWAY_FAILED_TRANSACTION_STORAGE_COLLECTION
from waves_gateway.model import FailedTransaction
from pymongo.collection import Collection  # type: ignore
from .failed_transaction_storage import FailedTransactionStorage


@Injectable(deps=[GATEWAY_FAILED_TRANSACTION_STORAGE_COLLECTION], provides=FailedTransactionStorage)
class FailedTransactionStorageImpl(FailedTransactionStorage):
    """
    FailedTransaction MongoDB implementation
    """

    def __init__(self, collection: Collection) -> None:
        self._collection = collection

    def save_failed_transaction(self, failed_tx: FailedTransaction) -> None:
        """
        Save an exception in a mongoDB collection
        """
        result = self.get_failed_transaction_by_tx(failed_tx.transaction["tx"])

        if not result:
            self._collection.insert_one(self._failed_transaction_as_dict(failed_tx))

    def get_failed_transactions(self):
        """
        inherit
        """
        cursor = self._collection.find()

        res = []

        for each in cursor:
            res.append(self._failed_transaction_as_dict(self._cursor_as_failed_transaction(each)))
        return res

    def get_failed_transaction_by_tx(self, tx):
        """
        inherit
        """
        cursor = self._collection.find({"transaction.tx": tx})

        res = []

        for each in cursor:
            res.append(self._failed_transaction_as_dict(self._cursor_as_failed_transaction(each)))
        return res

    def _failed_transaction_as_dict(self, failed_transaction: FailedTransaction) -> dict:
        """
        inherit
        """
        res = dict()

        res[FailedTransaction.DICT_ID] = failed_transaction.id
        res[FailedTransaction.DICT_CURRENCY] = failed_transaction.currency
        res[FailedTransaction.DICT_CAUSE] = failed_transaction.cause
        res[FailedTransaction.DICT_MESSAGE] = failed_transaction.message
        res[FailedTransaction.DICT_DATE] = failed_transaction.date
        res[FailedTransaction.DICT_TRANSACTION] = failed_transaction.transaction

        if failed_transaction.back_transfer_attemptlist:
            res[FailedTransaction.DICT_BACK_TRANSFER_ATTEMPTLIST] = failed_transaction.back_transfer_attemptlist

        return res

    def _cursor_as_failed_transaction(self, cursor):
        """
        inherit
        """
        failed_t = FailedTransaction(cursor[FailedTransaction.DICT_CURRENCY], cursor[FailedTransaction.DICT_CAUSE],
                                     cursor[FailedTransaction.DICT_MESSAGE], cursor[FailedTransaction.DICT_DATE],
                                     cursor[FailedTransaction.DICT_TRANSACTION], None,
                                     cursor[FailedTransaction.DICT_ID])
        if FailedTransaction.DICT_BACK_TRANSFER_ATTEMPTLIST in cursor:
            failed_t.back_transfer_attemptlist = cursor[FailedTransaction.DICT_BACK_TRANSFER_ATTEMPTLIST]

        return failed_t
