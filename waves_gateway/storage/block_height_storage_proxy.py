"""
BlockHeightStorageProxy
"""

from abc import ABC, abstractmethod
from typing import Optional


class BlockHeightStorageProxy(ABC):
    """
    Storage for the Block height. This storage is an abstraction layer for the polling service
    and is not meant to be provided by the framework user.
    Internally, it forwards the requests to the KeyValueStorage.
    """

    @abstractmethod
    def get_last_checked_block_height(self) -> Optional[int]:
        """
        Returns the stored last checked block height or None if it was never set.
        """
        pass

    @abstractmethod
    def set_last_checked_block_height(self, block_height: int) -> None:
        """
        Overwrites the last checked block height.
        """
