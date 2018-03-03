"""
WalletStorage
"""

from abc import ABC, abstractmethod
from typing import Optional

from waves_gateway.model import KeyPair
from waves_gateway.common import DuplicateSecretError


class WalletStorage(ABC):
    """
    Storage for private keys.
    """

    @abstractmethod
    def get_secret_by_public_address(self, public_address: str) -> Optional[KeyPair]:
        """
        Returns the secret that is associated to the given public address or None if no such secret exists.
        """
        pass

    def public_address_exists(self, public_address: str) -> bool:
        """
        Returns whether there is an entry with an CoinAddressSecret that has the given public public_address.
        """
        return self.get_secret_by_public_address(public_address) is not None

    @abstractmethod
    def save_address_secret(self, secret: KeyPair) -> None:
        """
        Stores the given address secret.
        """
        pass

    def safely_save_address_secret(self, secret: KeyPair) -> None:
        """
        Before inserting the given secret, the method tests if the public address of the secret is already
        listed in the database. If so, an DuplicateSecretError will be thrown.
        """
        if not self.public_address_exists(secret.public):
            return self.save_address_secret(secret)
        else:
            raise DuplicateSecretError(address=secret.public)
