"""
MapStorage
"""

from abc import ABC, abstractmethod
from typing import Optional

from waves_gateway.model import MappingEntry
from waves_gateway.common import DuplicateMappingError
import gevent.lock


class MapStorage(ABC):
    """
    Storage that is capable of saving querying instances of MappingEntry.
    """

    def __init__(self):
        self._lock = gevent.lock.Semaphore()

    def coin_address_exists(self, coin_address: str) -> bool:
        """
        Tests if the given coin_address does belong to an mapping.
        This method may be overwritten if a more performant variant exists.
        """
        return self.get_waves_address_by_coin_address(coin_address) is not None

    @abstractmethod
    def get_waves_address_by_coin_address(self, coin_address: str) -> Optional[str]:
        """
        Returns the Waves address that is associated to the given custom currency address.
        May return none, if no such mapping exists.
        """
        pass

    @abstractmethod
    def get_coin_address_by_waves_address(self, coin_address: str) -> Optional[str]:
        """
        Returns the custom currency address that is associated to the given Waves address.
        May return none, if no such mapping exists.
        """
        pass

    def waves_address_exists(self, waves_address: str) -> bool:
        """
        Tests if the given Waves address exists.
        This method may be overwritten if a more performant variant exists.
        """
        return self.get_coin_address_by_waves_address(waves_address) is not None

    @abstractmethod
    def save_mapping(self, mapping: MappingEntry):
        """
        Stores the given mapping.
        """
        pass

    def safely_save_mapping(self, mapping: MappingEntry):
        """
        Checks if the given mapping exists, before it is saved.
        If the mapping does already exist, an DuplicateMappingError is thrown.
        """
        self._lock.acquire()

        try:
            if self.waves_address_exists(mapping.waves_address) or self.coin_address_exists(mapping.coin_address):
                raise DuplicateMappingError()

            res = self.save_mapping(mapping)

            self._lock.release()
        finally:
            self._lock.release()

        return res
