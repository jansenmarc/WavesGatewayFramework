"""
TransactionService
"""

from abc import ABC, abstractmethod
from typing import Optional

from waves_gateway.model import Transaction, TransactionAttempt


class TransactionService(ABC):
    """
    Defines the functionality of a service that can be used to perform a specific TransactionAttempt.
    """

    @abstractmethod
    def send_coin(self, attempt: TransactionAttempt, secret: Optional[str]) -> Transaction:
        """
        Sends a specific amount of coins and returns the resulting transaction.
        The sender address/account looses (amount + fee) coins.
        """
        pass
