import unittest
from typing import cast
from unittest.mock import MagicMock, patch
from pymongo.collection import Collection  # type: ignore
from waves_gateway.model import TransactionAttemptList, AttemptListTrigger, TransactionSender, TransactionAttempt, \
    TransactionAttemptReceiver, AttemptListQuery

from waves_gateway.serializer import TransactionAttemptListSerializer

from waves_gateway.storage import MongoTransactionAttemptListStorageImpl


class MongoTransactionAttemptListStorageImplSpec(unittest.TestCase):
    def setUp(self):
        self._serializer = MagicMock()
        self._collection = MagicMock()
        self._limit = 2
        self._max_tries = 30

        self._storage = MongoTransactionAttemptListStorageImpl(
            collection=cast(Collection, self._collection),
            serializer=cast(TransactionAttemptListSerializer, self._serializer),
            limit=self._limit,
            max_tries=self._max_tries)

    def test_get_attempt_list_id_not_found(self):
        mock_id = "26739887"
        expected_dict = dict()
        expected_dict[TransactionAttemptList.DICT_ID] = mock_id

        self._collection.find_one.return_value = None

        self.assertIsNone(self._storage.find_by_attempt_list_id(mock_id))

        self._collection.find_one.assert_called_once_with(expected_dict)

    def test_get_attempt_list_id_found_result(self):
        mock_id = "26739887"
        mock_result = MagicMock()
        mock_from_dict_result = MagicMock()
        expected_dict = dict()
        expected_dict[TransactionAttemptList.DICT_ID] = mock_id

        self._collection.find_one.return_value = mock_result
        self._serializer.attempt_list_from_dict.return_value = mock_from_dict_result

        res = self._storage.find_by_attempt_list_id(mock_id)

        self.assertEqual(res, mock_from_dict_result)
        self._collection.find_one.assert_called_once_with(expected_dict)

    def test_attempt_list_id_exists_success(self):
        mock_id = "729872385"

        with patch.object(self._storage, 'find_by_attempt_list_id'):
            self._storage.find_by_attempt_list_id.return_value = MagicMock()
            self.assertTrue(self._storage.attempt_list_id_exists(mock_id))
            self._storage.find_by_attempt_list_id.assert_called_once_with(mock_id)

    def test_attempt_list_id_exists_failure(self):
        mock_id = "729872385"

        with patch.object(self._storage, 'find_by_attempt_list_id'):
            self._storage.find_by_attempt_list_id.return_value = None
            self.assertFalse(self._storage.attempt_list_id_exists(mock_id))
            self._storage.find_by_attempt_list_id.assert_called_once_with(mock_id)

    def test_find_by_trigger_senders_is_none_found_result(self):
        mock_find_one_result = MagicMock()
        mock_from_dict_result = MagicMock()
        trigger = AttemptListTrigger(tx="72935687", receiver=3, currency="2793658", senders=None)
        expected_query = dict()
        expected_query[TransactionAttemptList.DICT_TRIGGER + "." + AttemptListTrigger.DICT_RECEIVER] = trigger.receiver
        expected_query[TransactionAttemptList.DICT_TRIGGER + "." + AttemptListTrigger.DICT_CURRENCY] = trigger.currency
        expected_query[TransactionAttemptList.DICT_TRIGGER + "." + AttemptListTrigger.DICT_TX] = trigger.tx

        self._serializer.attempt_list_from_dict.return_value = mock_from_dict_result
        self._collection.find_one.return_value = mock_find_one_result

        res = self._storage.find_by_trigger(trigger)

        self.assertEqual(res, mock_from_dict_result)
        self._collection.find_one.assert_called_once_with(expected_query)
        self._serializer.attempt_list_from_dict.assert_called_once_with(mock_find_one_result)

    def test_find_by_trigger_senders_is_none_not_found(self):
        trigger = AttemptListTrigger(tx="72935687", receiver=3, currency="2793658", senders=None)
        expected_query = dict()
        expected_query[TransactionAttemptList.DICT_TRIGGER + "." + AttemptListTrigger.DICT_RECEIVER] = trigger.receiver
        expected_query[TransactionAttemptList.DICT_TRIGGER + "." + AttemptListTrigger.DICT_CURRENCY] = trigger.currency
        expected_query[TransactionAttemptList.DICT_TRIGGER + "." + AttemptListTrigger.DICT_TX] = trigger.tx

        self._collection.find_one.return_value = None

        res = self._storage.find_by_trigger(trigger)

        self.assertIsNone(res)
        self._collection.find_one.assert_called_once_with(expected_query)
        self._serializer.attempt_list_from_dict.assert_not_called()

    def test_save_attempt_list(self):
        mock_attempt_list = MagicMock()
        mock_as_dict_result = MagicMock()

        self._serializer.attempt_list_as_dict.return_value = mock_as_dict_result

        self._storage.save_attempt_list(cast(TransactionAttemptList, mock_attempt_list))

        self._serializer.attempt_list_as_dict.assert_called_once_with(mock_attempt_list)
        self._collection.insert_one.assert_called_once_with(mock_as_dict_result)

    def test_trigger_exists_success(self):
        mock_find_by_trigger_result = MagicMock()
        mock_trigger = MagicMock()

        with patch.object(self._storage, 'find_by_trigger'):
            self._storage.find_by_trigger.return_value = mock_find_by_trigger_result
            res = self._storage.trigger_exists(cast(AttemptListTrigger, mock_trigger))
            self._storage.find_by_trigger.assert_called_once_with(mock_trigger)
            self.assertTrue(res)

    def test_trigger_exists_failure(self):
        mock_trigger = MagicMock()

        with patch.object(self._storage, 'find_by_trigger'):
            self._storage.find_by_trigger.return_value = None
            res = self._storage.trigger_exists(cast(AttemptListTrigger, mock_trigger))
            self._storage.find_by_trigger.assert_called_once_with(mock_trigger)
            self.assertFalse(res)

    def test_update_attempt_list(self):
        trigger = AttemptListTrigger(
            tx="792873", receiver=1, currency="waves", senders=[TransactionSender(address="723789")])

        attempt_list = TransactionAttemptList(
            trigger=trigger,
            attempts=[
                TransactionAttempt(
                    currency="coin",
                    fee=100,
                    receivers=[TransactionAttemptReceiver(address="973846", amount=234)],
                    sender="739264857")
            ])

        expected_query = dict()
        expected_query[TransactionAttemptList.DICT_ID] = attempt_list.attempt_list_id
        mock_find_one_result = MagicMock()
        mock_attempt_list_as_dict_result = MagicMock()

        self._collection.find_one_and_replace.return_value = mock_find_one_result
        self._serializer.attempt_list_as_dict.return_value = mock_attempt_list_as_dict_result

        self._storage.update_attempt_list(attempt_list)

        self._collection.find_one_and_replace.assert_called_once_with(expected_query, mock_attempt_list_as_dict_result)
        self._serializer.attempt_list_as_dict.assert_called_once_with(attempt_list)

    def test_gateway_transaction_exists_success(self):
        mock_transaction = "7326847"
        expected_query = dict()
        expected_query[TransactionAttemptList.DICT_TRANSACTIONS] = mock_transaction
        mock_find_one_result = MagicMock()

        self._collection.find_one.return_value = mock_find_one_result

        res = self._storage.gateway_transaction_exists(mock_transaction)

        self._collection.find_one.assert_called_once_with(expected_query)
        self.assertTrue(res)

    def test_gateway_transaction_exists_failure(self):
        mock_transaction = "7326847"
        expected_query = dict()
        expected_query[TransactionAttemptList.DICT_TRANSACTIONS] = mock_transaction

        self._collection.find_one.return_value = None

        res = self._storage.gateway_transaction_exists(mock_transaction)

        self._collection.find_one.assert_called_once_with(expected_query)
        self.assertFalse(res)

    def test_query_by_anything(self):
        expected_query = dict()
        expected_sub_query = dict()
        expected_query['$or'] = list()
        expected_query['$or'].append(expected_sub_query)
        expected_sub_query['$or'] = list()
        mock_anything = "7239874"

        trigger_tx_query = dict()
        trigger_tx_query[TransactionAttemptList.DICT_TRIGGER + "." + AttemptListTrigger.DICT_TX] = mock_anything

        attempt_list_id_query = dict()
        attempt_list_id_query[TransactionAttemptList.DICT_ID] = mock_anything

        transaction_query = dict()
        transaction_query[TransactionAttemptList.DICT_TRANSACTIONS] = mock_anything

        senders_query = dict()
        senders_subquery = dict()
        senders_subquery[TransactionSender.DICT_ADDRESS_KEY] = mock_anything
        senders_query[TransactionAttemptList.DICT_TRIGGER + '.' +
                      AttemptListTrigger.DICT_SENDERS_KEY] = senders_subquery

        expected_sub_query['$or'].append(trigger_tx_query)
        expected_sub_query['$or'].append(attempt_list_id_query)
        expected_sub_query['$or'].append(transaction_query)
        expected_sub_query['$or'].append(senders_query)

        mock_find_result = MagicMock()
        mock_limit_result = MagicMock()
        mock_find_result.limit.return_value = [mock_limit_result]
        mock_attempt_list_from_dict_result = MagicMock()

        self._collection.find.return_value = mock_find_result
        self._serializer.attempt_list_from_dict.return_value = mock_attempt_list_from_dict_result

        attempt_list_query = AttemptListQuery(anything=mock_anything)

        res = self._storage.query_attempt_lists(attempt_list_query)

        self.assertEqual(res, [mock_attempt_list_from_dict_result])
        self._collection.find.assert_called_once_with(expected_query)
        mock_find_result.limit.assert_called_once_with(self._limit)

    def test_tries_query(self):
        expected_all_tries_query = {"$where": "this.tries > 1"}
        expected_two_tries_query = {"$where": "this.tries ==2"}

        self.assertEqual(expected_all_tries_query, self._storage._create_tries_query(""))
        self.assertEqual(expected_two_tries_query, self._storage._create_tries_query("2"))

    def test_attempts_query(self):
        expected_all_attempts_query = {"$where": "this.attempts.length > 1"}
        expected_two_attempts_query = {"$where": "this.attempts.length ==2"}

        self.assertEqual(expected_all_attempts_query, self._storage._create_attempt_query(""))
        self.assertEqual(expected_two_attempts_query, self._storage._create_attempt_query("2"))
