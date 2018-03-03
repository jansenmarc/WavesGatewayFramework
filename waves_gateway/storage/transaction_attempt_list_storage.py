"""
TransactionAttemptListStorage
"""

from abc import ABC, abstractmethod
from typing import Optional, List

import gevent.lock

from waves_gateway.common import DuplicateAttemptListTriggerError, DuplicateAttemptListIDError
from waves_gateway.model import TransactionAttemptList, AttemptListTrigger, AttemptListQuery


class TransactionAttemptListStorage(ABC):
    """
    Defines what an storage for TransactionAttemptList instances must be capable of.
    """

    def __init__(self):
        self._save_lock = gevent.lock.Semaphore()

    @abstractmethod
    def find_by_trigger(self, trigger: AttemptListTrigger) -> Optional[TransactionAttemptList]:
        """
        Finds a specific attempt_list by its trigger.
        """
        pass

    @abstractmethod
    def find_by_attempt_list_id(self, attempt_list_id: str) -> Optional[TransactionAttemptList]:
        """
        Finds a specific attempt_list by its trigger.
        """
        pass

    @abstractmethod
    def trigger_exists(self, trigger: AttemptListTrigger) -> bool:
        """
        Tests if an attempt_list with the given trigger exists.
        """
        pass

    @abstractmethod
    def attempt_list_id_exists(self, attempt_list_id: str) -> bool:
        """
        Tests if an attempt_list with the given id exists.
        """
        pass

    @abstractmethod
    def gateway_transaction_exists(self, tx: str) -> bool:
        """
        Tests if a given transaction identifier exists.
        """
        pass

    @abstractmethod
    def save_attempt_list(self, attempt_list: TransactionAttemptList) -> None:
        """
        Creates a new attempt_list.
        """
        pass

    def safely_save_attempt_list(self, attempt_list: TransactionAttemptList) -> None:
        """
        Creates a new attempt_list. Throws an exception if the id or the trigger already exist.
        """
        self._save_lock.acquire()

        try:
            if self.trigger_exists(attempt_list.trigger):
                raise DuplicateAttemptListTriggerError()

            if self.attempt_list_id_exists(attempt_list.attempt_list_id):
                raise DuplicateAttemptListIDError()

            self.save_attempt_list(attempt_list)
            self._save_lock.release()
        finally:
            self._save_lock.release()

    @abstractmethod
    def update_attempt_list(self, attempt_list: TransactionAttemptList) -> None:
        """
        Updates an existing attempt_list.
        """
        pass

    @abstractmethod
    def query_attempt_lists(self, query: AttemptListQuery) -> List[TransactionAttemptList]:
        """
        Searches for attempt lists by the given criteria.
        """
        pass

    @abstractmethod
    def find_oldest_pending_attempt_list(self) -> Optional[TransactionAttemptList]:
        """
        Queries for the oldest attempt list that is not complete.
        """
        pass
