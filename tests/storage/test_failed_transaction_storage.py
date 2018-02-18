import unittest
from typing import cast
from unittest.mock import MagicMock

from pymongo.collection import Collection  # type: ignore

from waves_gateway.model import FailedTransaction
from waves_gateway.storage import FailedTransactionStorageImpl


class FailedTransactionStorageImplTest(unittest.TestCase):
    def setUp(self):
        self._collection = MagicMock()

        self._failed_tx_storage = FailedTransactionStorageImpl(collection=cast(Collection, self._collection))

    def test_save_failed_transaction(self):
        failed_tx = FailedTransaction("1", "waves", "amount too small", "msg", "", {"tx": "12345"},
                                      "back transfer attemptlist id")
        self._failed_tx_storage.save_failed_transaction(failed_tx)
        self._collection.find.return_value = None
        self._collection.insert_one.assert_called_once_with({
            'failed_transaction_id': '1',
            'currency': 'waves',
            'reason': 'amount too small',
            'message': 'msg',
            'date': '',
            'transaction': {
                'tx': '12345'
            },
            'back_transfer_attemptlist': 'back transfer attemptlist id'
        })

    def test_get_failed_transactions(self):
        self._failed_tx_storage.get_failed_transaction_by_tx("123456")
        self._collection.find.assert_called_once_with({"transaction.tx": "123456"})

    def test_failed_transaction_as_dict(self):
        failed_tx = FailedTransaction("1", "waves", "amount too small", "msg", "", {"tx": "12345"},
                                      "back transfer attemptlist id")
        tx_as_dict = self._failed_tx_storage._failed_transaction_as_dict(failed_tx)
        self.assertEqual(
            tx_as_dict, {
                'failed_transaction_id': '1',
                'currency': 'waves',
                'reason': 'amount too small',
                'message': 'msg',
                'date': '',
                'transaction': {
                    'tx': '12345'
                },
                'back_transfer_attemptlist': 'back transfer attemptlist id'
            })
