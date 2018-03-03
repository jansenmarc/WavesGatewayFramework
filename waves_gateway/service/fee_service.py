"""
FeeService
"""

from abc import ABC, abstractmethod
from typing import Union

import pywaves  # type: ignore
from decimal import Decimal


class FeeService(ABC):
    """
    Defines the fee values, the Gateway requires. The waves_fee may also be overwritten of required.
    """

    @abstractmethod
    def get_coin_fee(self) -> Union[int, Decimal]:
        pass

    @abstractmethod
    def get_gateway_fee(self) -> Union[int, Decimal]:
        pass

    def get_waves_fee(self) -> int:
        return pywaves.DEFAULT_TX_FEE
