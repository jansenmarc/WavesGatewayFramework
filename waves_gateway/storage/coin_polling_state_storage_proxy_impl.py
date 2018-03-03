"""CoinPollingStateStorageProxyImpl"""

from waves_gateway.common import Injectable
from waves_gateway.model import PollingState
from .polling_state_storage_proxy import PollingStateStorageProxy
from .key_value_storage import KeyValueStorage


@Injectable(deps=[KeyValueStorage])
class CoinPollingStateStorageProxyImpl(PollingStateStorageProxy):
    """Forwards polling_state requests to the coin methods of KeyValueStorage."""

    def __init__(self, key_value_storage: KeyValueStorage) -> None:
        self._storage = key_value_storage

    def set_polling_state(self, state: PollingState) -> None:
        self._storage.set_coin_polling_state(state)

    def get_polling_state(self) -> PollingState:
        return self._storage.get_coin_polling_state()
