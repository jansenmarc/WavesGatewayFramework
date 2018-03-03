"""PollingStateStorageProxy"""

from abc import ABC, abstractmethod
from waves_gateway.model import PollingState


class PollingStateStorageProxy(ABC):
    """Offers access to the current polling_state."""

    @abstractmethod
    def get_polling_state(self) -> PollingState:
        pass

    @abstractmethod
    def set_polling_state(self, state: PollingState) -> None:
        pass
