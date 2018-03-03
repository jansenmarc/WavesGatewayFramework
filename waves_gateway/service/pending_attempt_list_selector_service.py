"""
PendingAttemptListSelectorService
"""

from typing import Optional, List

from waves_gateway.common import Injectable
from waves_gateway.storage import TransactionAttemptListStorage
from waves_gateway.model import TransactionAttemptList
import gevent.lock as lock


@Injectable(deps=[TransactionAttemptListStorage])
class PendingAttemptListSelectorService(object):
    """
    This service must be a singleton in the application. It can be used by worker instances
    to acquire an attempt_list. While the attempt_list is being processed by the worker, it cannot be acquired by
    other workers. Once the worker releases the attempt_list, it may be acquired by other workers.
    So, this instance can be called a lock for attempt lists.
    The lock method is secured by a semaphore, so it cannot be called in parallel.
    """

    def __init__(self, attempt_list_storage: TransactionAttemptListStorage) -> None:
        self._attempt_list_storage = attempt_list_storage
        self._lock = lock.Semaphore()
        self._locked_attempt_lists = []  # type: List[str]

    def lock_attempt_list(self) -> Optional[TransactionAttemptList]:
        """
        Locks an attempt list, so that it can be processed.
        """
        self._lock.acquire()

        try:
            result = self._attempt_list_storage.find_oldest_pending_attempt_list()

            if result is not None and result.attempt_list_id not in self._locked_attempt_lists:
                self._locked_attempt_lists.append(result.attempt_list_id)
                result.increment_tries()
                self._attempt_list_storage.update_attempt_list(result)
            else:
                result = None

            self._lock.release()
        finally:
            self._lock.release()

        return result

    def release_attempt_list(self, attempt_list: TransactionAttemptList) -> None:
        """
        Releases an attempt list, so that other workers may work with the attempt list.
        """
        if attempt_list.attempt_list_id in self._locked_attempt_lists:
            self._locked_attempt_lists.remove(attempt_list.attempt_list_id)
