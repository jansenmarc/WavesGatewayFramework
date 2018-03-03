"""PollingTransactionStateSerializer"""
from typing import Any, Dict

from waves_gateway.common import Injectable
from waves_gateway.model import PollingTransactionState
from .serializer import Serializer


@Injectable()
class PollingTransactionStateSerializer(Serializer):
    """Defines how a PollingTransactionState can be serialized and deserialized."""

    def as_dict(self, value: PollingTransactionState) -> dict:
        res = dict()  # type: Dict[str, Any]

        res[PollingTransactionState.DICT_OK_KEY] = value.ok
        res[PollingTransactionState.DICT_TRIES_KEY] = value.tries

        return res

    def from_dict(self, data: dict) -> PollingTransactionState:
        return PollingTransactionState(
            ok=data[PollingTransactionState.DICT_OK_KEY], tries=data[PollingTransactionState.DICT_TRIES_KEY])
