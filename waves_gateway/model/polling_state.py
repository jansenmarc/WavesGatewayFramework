"""
PollingState
"""

from typing import Dict


class PollingTransactionState(object):
    """
    Stores information about a processed transaction.
    """

    DICT_TRIES_KEY = 'tries'
    DICT_OK_KEY = 'ok'

    def __init__(self, ok: bool = False, tries: int = 0) -> None:
        self._ok = ok
        self._tries = tries

    @property
    def tries(self) -> int:
        return self._tries

    @property
    def ok(self) -> bool:
        return self._ok

    def increment_tries(self) -> None:
        self._tries = self._tries + 1

    def mark_as_done(self):
        self._ok = True

    def __eq__(self, other):
        return self.tries == other.tries and self.ok == other.ok


class PollingState(object):
    """
    Saves information about the last poller execution.
    """

    DICT_TRANSACTION_MAP_KEY = 'transaction_map'

    def __init__(self, transaction_map: Dict[str, PollingTransactionState] = None) -> None:

        if transaction_map is None:
            self._transaction_map = dict()  # type: Dict[str, PollingTransactionState]
        else:
            self._transaction_map = transaction_map

    def __eq__(self, other):
        return self.transaction_map == other.transaction_map

    @property
    def transaction_map(self) -> Dict[str, PollingTransactionState]:
        return self._transaction_map
