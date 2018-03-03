"""
Exceptions
"""
from typing import Union

from decimal import Decimal


class ParseError(Exception):
    """
    Indicates that a parsing error occurred, for example when parsing JSON or dict.
    """
    pass


class InvalidConfigError(Exception):
    """
    Raised when the provided Gateway configuration is not valid
    and the Gateway can therefore not be constructed.
    """
    pass


class DuplicateMappingError(Exception):
    """
    Raised when the application tries to create a mapping that already exists.
    This should not happen which means that this is an internal error of the framework.
    """
    pass


class DuplicateSecretError(Exception):
    """
    Raised when the application tries to save a secret for the same address multiple times.
    This should not happen which means that this is an internal error of the framework.
    """

    def __init__(self, address: str) -> None:
        super().__init__("Attempted to store secret of address '" + address + "', but it already exists.")


class DuplicateTransactionError(Exception):
    """
    Raised when the application tries to create a transaction that already exists.
    This should not happen which means that this is an internal error of the framework.
    """

    def __init__(self, tx: str) -> None:
        super().__init__("Attempted to store transaction '" + tx + "', but it already exists.")


class MissingSecretError(Exception):
    """
    Raised when the application needs a specific secret, but it is not available.
    """

    def __init__(self, address: str) -> None:
        super().__init__("Did not found secret for address '" + address + "'. Cannot perform transaction.")


class AddressHasTooLessAmountError(Exception):
    """
    Raised when the application attempts to make a transaction, but the sender address has too less amount.
    """

    def __init__(self, expected_amount: Union[int, Decimal], real_amount: Union[int, Decimal], address: str) -> None:
        super().__init__("Expected the address '" + address + "' to contain at least an amount of " +
                         str(expected_amount) + ", but it only has an amount of " + str(real_amount))


class MappingNotFoundForCoinAddress(Exception):
    """
    Raised when a specific mapping was expected to exist, but not found.
    """

    def __init__(self, coin_address: str) -> None:
        super().__init__(
            "The address '" + coin_address + "' has no associated Waves address, but was expected to have one.")


class MultipleGatewayReceiversError(Exception):
    """
    Raised when the Gateway encounters a transaction with multiple receiver addresses.
    """

    def __init__(self, tx) -> None:
        super().__init__(
            "Encountered a transaction (" + tx + ") with multiple receiver addresses. The Gateway cannot handle this.")


class DuplicateAttemptListTriggerError(Exception):
    """
    Raised when trying to create another attempt_list with the same trigger.
    """
    pass


class DuplicateAttemptListIDError(Exception):
    """
    Raised when trying to create another attempt_list with the same identifier.
    """
    pass


class PyWavesError(Exception):
    """
    Raised when PyWaves encountered any error.
    """
    pass


class WavesAddressInvalidError(Exception):
    """
    Raised when an invalid waves address was overhanded.
    """
    pass


class InvalidTransactionIdentifier(Exception):
    """
    Raised when the transaction identifier is not part of the blockchain.
    """
    pass


class InjectorError(Exception):
    """
    Raised when a token could not be resolved for some reason.
    """
    pass


class WavesNodeException(Exception):
    """
    Raised when the waves node was unable to process the request for some reason.
    """

    def __init__(self, url: str, status_code: int, text: str) -> None:
        super().__init__(url + " " + str(status_code) + " " + text)
