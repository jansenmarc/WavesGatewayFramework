"""
GatewayValidationService
"""

from waves_gateway.model import KeyPair
from .address_validation_service import AddressValidationService
from waves_gateway.common import Injectable, InvalidConfigError, CUSTOM_CURRENCY_NAME, GATEWAY_OWNER_ADDRESS, \
    GATEWAY_COIN_ADDRESS_SECRET, GATEWAY_WAVES_ADDRESS_SECRET
from .waves_address_validation_service import WavesAddressValidationService
from .token import COIN_ADDRESS_VALIDATION_SERVICE


@Injectable(deps=[
    WavesAddressValidationService, COIN_ADDRESS_VALIDATION_SERVICE, GATEWAY_WAVES_ADDRESS_SECRET, GATEWAY_OWNER_ADDRESS,
    CUSTOM_CURRENCY_NAME, GATEWAY_COIN_ADDRESS_SECRET
])
class GatewayValidationService(object):
    """
    Implements validation methods that may be used the Gateway application. The validate_all_addresses is meant to
    be called right on initialization to prevent the usage of misleading addresses.
    """

    def __init__(self, waves_address_validation_service: AddressValidationService,
                 coin_address_validation_service: AddressValidationService, gateway_waves_address_secret: KeyPair,
                 gateway_owner_address: str, custom_currency_name: str, gateway_coin_address_secret: KeyPair) -> None:
        self._waves_address_validation_service = waves_address_validation_service
        self._coin_address_validation_service = coin_address_validation_service
        self._gateway_waves_address_secret = gateway_waves_address_secret
        self._gateway_owner_address = gateway_owner_address
        self._custom_currency_name = custom_currency_name
        self._gateway_coin_address_secret = gateway_coin_address_secret

    def validate_all_addresses(self):
        if not self._waves_address_validation_service.validate_address(self._gateway_waves_address_secret.public):
            raise InvalidConfigError("The public part of the given waves address "
                                     "KeyPair is not a valid waves address.")

        if not self._coin_address_validation_service.validate_address(self._gateway_owner_address):
            raise InvalidConfigError(
                "The gateway owner address is not a valid " + self._custom_currency_name + " address.")

        if not self._coin_address_validation_service.validate_address(self._gateway_coin_address_secret.public):
            raise InvalidConfigError(
                "The public part of the coin address is not a valid " + self._custom_currency_name + " address.")
