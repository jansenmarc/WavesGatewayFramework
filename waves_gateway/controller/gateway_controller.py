"""
GatewayController
"""

from abc import ABC, abstractmethod
from typing import Optional, List

from waves_gateway.model import AttemptListTrigger, TransactionAttemptList, AttemptListQuery


class GatewayController(ABC):
    """
    Defines the API for the Waves Client application.
    All possible interfaces should forward their requests to this abstract controller.
    """

    @abstractmethod
    def create_address(self, waves_address: str) -> str:
        """
        Returns a new address of the custom currency or an existing one
        if the waves_address is already associated to an address of the custom
        cryptocurrency.
        """
        pass

    @abstractmethod
    def get_attempt_list_by_trigger(self, trigger: AttemptListTrigger) -> Optional[TransactionAttemptList]:
        """
        Find an attempt_list by its trigger. The result may be None if no such trigger exists.
        """
        pass

    @abstractmethod
    def get_attempt_list_by_id(self, attempt_list_id: str) -> Optional[TransactionAttemptList]:
        """
        Find an attempt_list by its id. The result may be None if no such id exists.
        """
        pass

    @abstractmethod
    def query_attempt_lists(self, query: AttemptListQuery) -> List[TransactionAttemptList]:
        """
        Query attempt lists by specific criteria.
        """
        pass

    @abstractmethod
    def validate_waves_address(self, address: str) -> bool:
        """
        Tests if the given address is an valid waves address.
        """
        pass

    @abstractmethod
    def check_waves_transaction(self, tx: str) -> None:
        """
        Checks the given waves transaction whether it requires a new attempt list to be created.
        """
        pass

    @abstractmethod
    def check_coin_transaction(self, tx: str) -> None:
        """
        Checks the given coin transaction whether it requires a new attempt list to be created.
        """
        pass
