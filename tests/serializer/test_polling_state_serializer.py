from unittest import TestCase

from waves_gateway.model import PollingState, PollingTransactionState
from waves_gateway.serializer import PollingStateSerializer, Serializer, PollingTransactionStateSerializer


class PollingStateSerializerTest(TestCase):
    def setUp(self):
        self._polling_transaction_state_serializer = PollingTransactionStateSerializer()
        self._polling_state_serializer = PollingStateSerializer(
            polling_transaction_state_serializer=self._polling_transaction_state_serializer)  # type: Serializer

    def test_as_dict(self):
        polling_transaction_state = PollingTransactionState(ok=True, tries=3)

        polling_state = PollingState(transaction_map={'328964': polling_transaction_state})

        actual_result = self._polling_state_serializer.as_dict(polling_state)

        expected_result = dict()

        expected_transaction_state = dict()
        expected_transaction_state[PollingTransactionState.DICT_TRIES_KEY] = 3
        expected_transaction_state[PollingTransactionState.DICT_OK_KEY] = True

        expected_result[PollingState.DICT_TRANSACTION_MAP_KEY] = {'328964': expected_transaction_state}

        self.assertEqual(expected_result, actual_result)

    def test_from_dict(self):
        data = dict()

        transaction_state_data = dict()
        transaction_state_data[PollingTransactionState.DICT_TRIES_KEY] = 3
        transaction_state_data[PollingTransactionState.DICT_OK_KEY] = True

        data[PollingState.DICT_TRANSACTION_MAP_KEY] = {'328964': transaction_state_data}

        expected_transaction_state = PollingTransactionState(ok=True, tries=3)
        expected_polling_state = PollingState(transaction_map={'328964': expected_transaction_state})

        actual_polling_state = self._polling_state_serializer.from_dict(data)

        self.assertEqual(actual_polling_state, expected_polling_state)
