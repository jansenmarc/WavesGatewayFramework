"""
FailedTransactionStorage
"""
from waves_gateway.model import FailedTransaction
from abc import ABC, abstractmethod


class FailedTransactionStorage(ABC):
    """
    Storage for failed tx of the gateway
    """

    @abstractmethod
    def save_failed_transaction(self, failed_transaction: FailedTransaction) -> None:
        """
        Save a failed tx in a database
        """
        pass

    @abstractmethod
    def get_failed_transactions(self):
        """
        Get all failed transactions
        """
        pass

    @abstractmethod
    def _failed_transaction_as_dict(self, failed_transaction: FailedTransaction) -> dict:
        """
        Convert a FailedTransaction object to a dict
        """
        pass
