"""
KeyValueStorage
"""

from abc import ABC, abstractmethod
from typing import Optional
from waves_gateway.model import PollingState


class KeyValueStorage(ABC):
    """
    Storage for key-value pairs.
    """

    @abstractmethod
    def get_last_checked_coin_block_height(self) -> Optional[int]:
        """
        Returns the stored last checked coin block height or None if it was never set.
        """
        pass

    @abstractmethod
    def set_last_checked_coin_block_height(self, block_height: int) -> None:
        """
        Overwrites the last checked coin block height of the custom currency.
        """

    @abstractmethod
    def get_last_checked_waves_block_height(self) -> Optional[int]:
        """
        Returns the stored last checked waves block height or None if it was never set.
        """
        pass

    @abstractmethod
    def set_last_checked_waves_block_height(self, block_height: int) -> None:
        """
        Overwrites the last checked waves block height.
        """

    @abstractmethod
    def set_coin_polling_state(self, polling_state: PollingState) -> None:
        pass

    @abstractmethod
    def get_coin_polling_state(self) -> Optional[PollingState]:
        pass

    @abstractmethod
    def set_waves_polling_state(self, polling_state: PollingState) -> None:
        pass

    @abstractmethod
    def get_waves_polling_state(self) -> Optional[PollingState]:
        pass
