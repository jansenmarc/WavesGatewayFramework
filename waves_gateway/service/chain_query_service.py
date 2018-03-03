"""
ChainQueryService
"""

from abc import ABC, abstractmethod
from typing import List, Union, Optional

from decimal import Decimal

from waves_gateway.common import InjectionToken
from waves_gateway.model import Transaction


class ChainQueryService(ABC):
    """
    Provides read operations on the chain of the custom cryptocurrency
    """

    @abstractmethod
    def get_transactions_of_block_at_height(self, height: int) -> List[Transaction]:
        """
        Returns the transactions of the block at the given height.
        """
        pass

    @abstractmethod
    def get_height_of_highest_block(self) -> int:
        """
        Returns the newest block of the chain.
        """
        pass

    def get_coin_receiver_address_from_transaction(self, transaction: str):
        """
        Returns the raw (unparsed) receiver address string.
        """
        raise NotImplementedError()

    def get_transaction_by_tx(self, tx: str) -> Optional[Transaction]:
        """
        Returns the associated transaction if it exists. This functionality is optional.
        If the given identifier is invalid, the function should raise an InvalidTransactionIdentifier error.
        Otherwise, the return value None means that the transaction exists, but is not relevant for the Gateway.
        """
        raise NotImplementedError()
