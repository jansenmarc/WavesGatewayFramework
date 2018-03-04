import unittest
from typing import cast, Any
from unittest.mock import MagicMock

from waves_gateway.model import TransactionAttemptList, AttemptListTrigger, TransactionSender, TransactionAttempt, \
    TransactionReceiver, TransactionAttemptReceiver
from waves_gateway.service import AttemptListConverterService, IntegerConverterService


class AttemptListConverterServiceSpec(unittest.TestCase):
    def setUp(self):
        self._coin_integer_converter_service = MagicMock()
        self._asset_integer_converter_service = MagicMock()
        self._attempt_list_converter = AttemptListConverterService(
            coin_integer_converter_service=cast(IntegerConverterService, self._coin_integer_converter_service),
            asset_integer_converter_service=cast(IntegerConverterService, self._asset_integer_converter_service))

    def test_revert_attempt_list_conversion(self):
        trigger = AttemptListTrigger(
            tx="792873", receiver=1, currency="waves", senders=[TransactionSender(address="723789")])

        attempt_list = TransactionAttemptList(
            trigger=trigger,
            attempts=[
                TransactionAttempt(
                    currency="coin",
                    fee=100,
                    receivers=[
                        TransactionAttemptReceiver(address="973846", amount=234),
                        TransactionAttemptReceiver(address="9327468", amount=235)
                    ],
                    sender="739264857")
            ])

        expected_attempt_list = TransactionAttemptList(
            trigger=trigger,
            attempts=[
                TransactionAttempt(
                    currency="coin",
                    fee=0.1,
                    receivers=[
                        TransactionAttemptReceiver(address="973846", amount=0.234),
                        TransactionAttemptReceiver(address="9327468", amount=0.235)
                    ],
                    sender="739264857")
            ])

        def mock_converter(value: Any):
            return value / 1000

        self._coin_integer_converter_service.revert_amount_conversion.side_effect = mock_converter

        res = self._attempt_list_converter.revert_attempt_list_conversion(attempt_list)

        self.assertEqual(res, expected_attempt_list)
