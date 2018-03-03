"""
MongoTransactionAttemptListStorageImpl
"""

from typing import Optional, List

from waves_gateway.common import Injectable, ATTEMPT_LIST_MAX_COMPLETION_TRIES, \
    TRANSACTION_ATTEMPT_LIST_STORAGE_COLLECTION
from waves_gateway.model import TransactionAttemptList, AttemptListTrigger, AttemptListQuery, TransactionSender
from waves_gateway.storage.transaction_attempt_list_storage import TransactionAttemptListStorage
from waves_gateway.serializer import TransactionAttemptListSerializer
from pymongo.collection import Collection  # type: ignore
from doc_inherit import class_doc_inherit, method_doc_inherit  # type: ignore
import pymongo


@Injectable(
    deps=[
        TRANSACTION_ATTEMPT_LIST_STORAGE_COLLECTION, TransactionAttemptListSerializer, ATTEMPT_LIST_MAX_COMPLETION_TRIES
    ],
    provides=TransactionAttemptListStorage)
class MongoTransactionAttemptListStorageImpl(TransactionAttemptListStorage):
    """
    Implements a storage for TransactionAttemptList instances for a MongoDB database.
    """

    @method_doc_inherit
    def find_by_attempt_list_id(self, attempt_list_id: str) -> Optional[TransactionAttemptList]:
        """inherit"""
        query = dict()
        query[TransactionAttemptList.DICT_ID] = attempt_list_id

        res = self._collection.find_one(query)

        if res is None:
            return None
        else:
            return self._serializer.attempt_list_from_dict(res)

    @method_doc_inherit
    def attempt_list_id_exists(self, attempt_list_id: str) -> bool:
        return self.find_by_attempt_list_id(attempt_list_id) is not None

    @method_doc_inherit
    def find_by_trigger(self, trigger: AttemptListTrigger) -> Optional[TransactionAttemptList]:
        query = self._create_trigger_query(trigger)
        res = self._collection.find_one(query)

        if res is not None:
            return self._serializer.attempt_list_from_dict(res)
        else:
            return None

    def __init__(self,
                 collection: Collection,
                 serializer: TransactionAttemptListSerializer,
                 max_tries: int,
                 limit: int = 10) -> None:
        TransactionAttemptListStorage.__init__(self)
        self._serializer = serializer
        self._collection = collection
        self._limit = limit
        self._max_tries = max_tries

    # noinspection PyMethodMayBeStatic
    def _create_trigger_query(self, trigger: AttemptListTrigger):
        query = dict()

        query[TransactionAttemptList.DICT_TRIGGER + "." + AttemptListTrigger.DICT_RECEIVER] = trigger.receiver
        query[TransactionAttemptList.DICT_TRIGGER + "." + AttemptListTrigger.DICT_CURRENCY] = trigger.currency
        query[TransactionAttemptList.DICT_TRIGGER + "." + AttemptListTrigger.DICT_TX] = trigger.tx

        return query

    @method_doc_inherit
    def save_attempt_list(self, attempt_list: TransactionAttemptList) -> None:
        self._collection.insert_one(self._serializer.attempt_list_as_dict(attempt_list))

    @method_doc_inherit
    def trigger_exists(self, trigger: AttemptListTrigger) -> bool:
        res = self.find_by_trigger(trigger)
        return res is not None

    @method_doc_inherit
    def update_attempt_list(self, attempt_list: TransactionAttemptList) -> None:
        query = self._create_attempt_list_id_query(attempt_list.attempt_list_id)
        self._collection.find_one_and_replace(query, self._serializer.attempt_list_as_dict(attempt_list))

    @method_doc_inherit
    def gateway_transaction_exists(self, tx: str) -> bool:
        query = self._create_transaction_query(tx)
        return self._collection.find_one(query) is not None

    def _create_trigger_tx_query(self, trigger_tx: str) -> dict:
        query = dict()
        query[TransactionAttemptList.DICT_TRIGGER + "." + AttemptListTrigger.DICT_TX] = trigger_tx
        return query

    def _create_trigger_receiver_query(self, trigger_receiver: int) -> dict:
        query = dict()
        query[TransactionAttemptList.DICT_TRIGGER + "." + AttemptListTrigger.DICT_RECEIVER] = trigger_receiver
        return query

    def _create_trigger_currency_query(self, trigger_currency: str) -> dict:
        query = dict()
        query[TransactionAttemptList.DICT_TRIGGER + "." + AttemptListTrigger.DICT_CURRENCY] = trigger_currency
        return query

    def _create_attempt_list_id_query(self, attempt_list_id: str) -> dict:
        query = dict()
        query[TransactionAttemptList.DICT_ID] = attempt_list_id
        return query

    def _create_transaction_query(self, transaction: str) -> dict:
        query = dict()
        query[TransactionAttemptList.DICT_TRANSACTIONS] = transaction
        return query

    def _create_senders_query(self, sender: str) -> dict:
        query = dict()
        subquery = dict()
        subquery[TransactionSender.DICT_ADDRESS_KEY] = sender
        query[TransactionAttemptList.DICT_TRIGGER + '.' + AttemptListTrigger.DICT_SENDERS_KEY] = subquery
        return query

    @method_doc_inherit
    def query_attempt_lists(self, query: AttemptListQuery) -> List[TransactionAttemptList]:
        find_query = dict()  # type: dict

        find_query['$or'] = list()
        or_conditions = find_query['$or']  # type: List[dict]

        if query.trigger_receiver is not None:
            or_conditions.append(self._create_trigger_receiver_query(query.trigger_receiver))

        if query.trigger_currency is not None:
            or_conditions.append(self._create_trigger_currency_query(query.trigger_currency))

        if query.trigger_tx is not None:
            or_conditions.append(self._create_trigger_tx_query(query.trigger_tx))

        if query.anything is not None:
            sub_query = dict()  # type: dict
            sub_query['$or'] = list()
            sub_or_conditions = sub_query['$or']  # type: List[dict]

            sub_or_conditions.append(self._create_trigger_tx_query(query.anything))
            sub_or_conditions.append(self._create_attempt_list_id_query(query.anything))
            sub_or_conditions.append(self._create_transaction_query(query.anything))
            sub_or_conditions.append(self._create_senders_query(query.anything))

            or_conditions.append(sub_query)

        raw_results = self._collection.find(find_query).limit(self._limit)

        results = []

        for raw_result in raw_results:
            results.append(self._serializer.attempt_list_from_dict(raw_result))

        return results

    def find_oldest_pending_attempt_list(self) -> Optional[TransactionAttemptList]:
        query = {
            '$and': [{
                '$nor': [{
                    'attempts': {
                        '$size': 1
                    },
                    'transactions': {
                        '$size': 1
                    }
                }, {
                    'attempts': {
                        '$size': 2
                    },
                    'transactions': {
                        '$size': 2
                    }
                }, {
                    'attempts': {
                        '$size': 3
                    },
                    'transactions': {
                        '$size': 3
                    }
                }]
            }, {
                '$or': [{
                    'tries': {
                        '$lt': self._max_tries
                    }
                }, {
                    'tries': {
                        '$exists': False
                    }
                }]
            }]
        }

        results = list(
            self._collection.find(query).sort(TransactionAttemptList.DICT_LAST_MODIFIED, pymongo.ASCENDING).limit(1))

        if len(results) >= 1:
            return self._serializer.attempt_list_from_dict(results[0])
        else:
            return None
