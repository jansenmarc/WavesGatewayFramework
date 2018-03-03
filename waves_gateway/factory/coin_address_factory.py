"""
CoinAddressFactory
"""

from abc import ABC, abstractmethod
from typing import Union

from waves_gateway.model import KeyPair


class CoinAddressFactory(ABC):
    """
    Offers the functionality to create new addresses in the custom currency.
    """

    @abstractmethod
    def create_address(self) -> Union[KeyPair, str]:
        """
        Create a new address.
        :return: The return type depends on the existence of an account. If there is an account, it may
        be sufficient to just return the public address. If not, the secret must be returned.
        """
        pass
