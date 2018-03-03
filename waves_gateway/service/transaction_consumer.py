"""
TransactionConsumer
"""

from abc import ABC, abstractmethod

from waves_gateway.model import Transaction


class TransactionConsumer(ABC):
    """
    Consumer of polled transactions
    """

    def filter_transaction(self, transaction: Transaction) -> bool:
        """
        Optional filter that shall be applied on the transactions that are overhanded to the
        handle_transaction method. Allows all transactions by default.
        """
        return True

    @abstractmethod
    def handle_transaction(self, transaction: Transaction) -> None:
        """
        Gets overhanded filtered transactions.
        """
        pass
