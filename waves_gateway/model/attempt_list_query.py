"""
AttemptListQuery
"""

from typing import Optional


class AttemptListQuery(object):
    """
    An AttemptListQuery summarizes parameters that can be used to search for an TransactionAttemptList.
    """

    def __init__(self,
                 trigger_tx: Optional[str] = None,
                 trigger_currency: Optional[str] = None,
                 trigger_receiver: Optional[int] = None,
                 anything: Optional[str] = None) -> None:
        self._trigger_tx = trigger_tx
        self._trigger_currency = trigger_currency
        self._trigger_receiver = trigger_receiver
        self._anything = anything

    @property
    def trigger_tx(self) -> str:
        return self._trigger_tx

    @property
    def trigger_currency(self) -> str:
        return self._trigger_currency

    @property
    def trigger_receiver(self) -> int:
        return self._trigger_receiver

    @property
    def anything(self) -> str:
        """
        This is a string, the user has entered which could be possibly anything.
        Try to find the best match.
        """
        return self._anything

    def __eq__(self, other):
        res = True

        res = res and self.anything == other.anything
        res = res and self.trigger_tx == other.trigger_tx
        res = res and self.trigger_currency == other.trigger_currency
        res = res and self.trigger_receiver == other.trigger_receiver

        return res
