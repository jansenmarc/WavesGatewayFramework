"""
AddressValidationService
"""

from abc import ABC, abstractmethod


class AddressValidationService(ABC):
    """
    Allows the validation of an address of a specific cryptocurrency.
    """

    @abstractmethod
    def validate_address(self, address: str) -> bool:
        """
        Should return true or false whether the given string is a valid address.
        """
        pass
