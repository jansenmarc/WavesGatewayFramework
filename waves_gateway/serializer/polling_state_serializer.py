"""PollingStateSerializer"""

from typing import Dict
from waves_gateway.common import Injectable
from waves_gateway.model import PollingState, PollingTransactionState
from .polling_transaction_state_serializer import PollingTransactionStateSerializer
from .serializer import Serializer


@Injectable(deps=[PollingTransactionStateSerializer])
class PollingStateSerializer(Serializer):
    """Defines how a PollingState can be serialized and deserialized."""

    def __init__(self, polling_transaction_state_serializer: PollingTransactionStateSerializer) -> None:
        self._polling_transaction_state_serializer = polling_transaction_state_serializer

    def _transaction_map_as_dict(self, transaction_map: Dict[str, PollingTransactionState]) -> dict:
        res = dict()

        for transaction in transaction_map:
            res[transaction] = self._polling_transaction_state_serializer.as_dict(transaction_map[transaction])

        return res

    def _transaction_map_from_dict(self, data: dict) -> Dict[str, PollingTransactionState]:
        res = dict()

        for transaction in data:
            res[transaction] = self._polling_transaction_state_serializer.from_dict(data[transaction])

        return res

    def as_dict(self, polling_state: PollingState) -> dict:
        res = dict()

        res[PollingState.DICT_TRANSACTION_MAP_KEY] = self._transaction_map_as_dict(polling_state.transaction_map)

        return res

    def from_dict(self, data: dict) -> PollingState:
        return PollingState(
            transaction_map=self._transaction_map_from_dict(data[PollingState.DICT_TRANSACTION_MAP_KEY]))
