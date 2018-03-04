import unittest
from unittest.mock import patch, MagicMock

from waves_gateway.service import WavesAddressValidationService


class WavesAddressValidationServiceTest(unittest.TestCase):
    def setUp(self):
        self._validation_service = WavesAddressValidationService()

    @patch('pywaves.Address', autospec=True)
    def test_validate_address_success(self, mock_address_class: MagicMock):

        mock_address = "3246789326"

        self.assertTrue(self._validation_service.validate_address(mock_address))

        mock_address_class.assert_called_once_with(address=mock_address)

    @patch('pywaves.Address', autospec=True)
    def test_validate_address_failure(self, mock_address_class: MagicMock):

        mock_address = "3246789326"

        def address_class_side_effect(address: str):
            raise ValueError()

        mock_address_class.side_effect = address_class_side_effect

        self.assertFalse(self._validation_service.validate_address(mock_address))

        mock_address_class.assert_called_once_with(address=mock_address)
