from unittest import TestCase
from unittest.mock import MagicMock
from waves_gateway.common import KeyPair, InvalidConfigError
from waves_gateway.service import GatewayValidationService


class TestGatewayValidation(TestCase):
    def setUp(self):
        self._waves_address_validation_service = MagicMock()
        self._coin_address_validation_service = MagicMock()
        self._gateway_waves_address_secret = KeyPair("7829657843", "8723657")
        self._gateway_owner_address = "78362487423"
        self._base_currency_name = "Turtle Network"
        self._custom_currency_name = "test_coin"
        self._gateway_coin_address_secret = KeyPair("68762375", "798234672")

        self._gateway_validation_service = GatewayValidationService(
            waves_address_validation_service=self._waves_address_validation_service,
            coin_address_validation_service=self._coin_address_validation_service,
            gateway_waves_address_secret=self._gateway_waves_address_secret,
            gateway_owner_address=self._gateway_owner_address,
            base_currency_name=self._base_currency_name,
            custom_currency_name=self._custom_currency_name,
            gateway_coin_address_secret=self._gateway_coin_address_secret)

    def test_should_success_if_all_valid(self):
        self._waves_address_validation_service.validate_address.return_value = True
        self._coin_address_validation_service.validate_address.return_value = True

        self._gateway_validation_service.validate_all_addresses()

        self._waves_address_validation_service.validate_address.assert_called_once_with(
            self._gateway_waves_address_secret.public)
        self._coin_address_validation_service.validate_address.assert_any_call(self._gateway_coin_address_secret.public)
        self._coin_address_validation_service.validate_address.assert_any_call(self._gateway_owner_address)

    def test_should_fail_if_gateway_waves_invalid(self):
        self._waves_address_validation_service.validate_address.return_value = False
        self._coin_address_validation_service.validate_address.return_value = True

        with self.assertRaises(InvalidConfigError):
            self._gateway_validation_service.validate_all_addresses()

    def test_should_fail_if_gateway_owner_invalid(self):
        self._waves_address_validation_service.validate_address.return_value = True

        def coin_validate_address(address: str):
            return address is not self._gateway_owner_address

        self._coin_address_validation_service.validate_address.side_effect = coin_validate_address

        with self.assertRaises(InvalidConfigError):
            self._gateway_validation_service.validate_all_addresses()

    def test_should_fail_if_gateway_coin_invalid(self):
        self._waves_address_validation_service.validate_address.return_value = True

        def coin_validate_address(address: str):
            return address is not self._gateway_coin_address_secret.public

        self._coin_address_validation_service.validate_address.side_effect = coin_validate_address

        with self.assertRaises(InvalidConfigError):
            self._gateway_validation_service.validate_all_addresses()
