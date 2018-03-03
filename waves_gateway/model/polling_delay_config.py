"""
PollingDelayConfig
"""
from typing import Any


class PollingDelayConfig(object):
    """
    Summarized configuration for the polling_delay settings in the Gateway Application.
    """

    DEFAULT_MIN_TRANSACTION_POLLING_DELAY_S = 0.0
    DEFAULT_MAX_TRANSACTION_POLLING_DELAY_S = 60.0
    DEFAULT_MIN_ATTEMPT_LIST_WORKER_DELAY_S = 0.1
    DEFAULT_MAX_ATTEMPT_LIST_WORKER_DELAY_S = 60.0

    def __init__(self,
                 coin_min_polling_delay_s: float = DEFAULT_MIN_TRANSACTION_POLLING_DELAY_S,
                 coin_max_polling_delay_s: float = DEFAULT_MAX_TRANSACTION_POLLING_DELAY_S,
                 waves_min_polling_delay_s: float = DEFAULT_MIN_TRANSACTION_POLLING_DELAY_S,
                 waves_max_polling_delay_s: float = DEFAULT_MAX_TRANSACTION_POLLING_DELAY_S,
                 attempt_list_worker_min_polling_delay_s: float = DEFAULT_MIN_ATTEMPT_LIST_WORKER_DELAY_S,
                 attempt_list_worker_max_polling_delay_s: float = DEFAULT_MAX_ATTEMPT_LIST_WORKER_DELAY_S) -> None:
        self._coin_polling_delay_s_min = coin_min_polling_delay_s
        self._coin_polling_delay_s_max = coin_max_polling_delay_s
        self._waves_polling_delay_s_min = waves_min_polling_delay_s
        self._waves_polling_delay_s_max = waves_max_polling_delay_s
        self._attempt_list_worker_min_polling_delay_s = attempt_list_worker_min_polling_delay_s
        self._attempt_list_worker_max_polling_delay_s = attempt_list_worker_max_polling_delay_s

    @staticmethod
    def from_single_polling_delay(polling_delay_s: float) -> Any:
        return PollingDelayConfig(
            coin_min_polling_delay_s=polling_delay_s,
            coin_max_polling_delay_s=polling_delay_s,
            waves_min_polling_delay_s=polling_delay_s,
            waves_max_polling_delay_s=polling_delay_s,
            attempt_list_worker_min_polling_delay_s=polling_delay_s,
            attempt_list_worker_max_polling_delay_s=polling_delay_s)

    @property
    def waves_max_polling_delay_s(self) -> float:
        return self._waves_polling_delay_s_max

    @property
    def waves_min_polling_delay_s(self) -> float:
        return self._waves_polling_delay_s_min

    @property
    def coin_min_polling_delay_s(self) -> float:
        return self._coin_polling_delay_s_min

    @property
    def coin_max_polling_delay_s(self) -> float:
        return self._coin_polling_delay_s_max

    @property
    def attempt_list_worker_min_polling_delay_s(self) -> float:
        return self._attempt_list_worker_min_polling_delay_s

    @property
    def attempt_list_worker_max_polling_delay_s(self) -> float:
        return self._attempt_list_worker_max_polling_delay_s
