import unittest
from unittest.mock import patch

from waves_gateway.model import Transaction, TransactionReceiver

from waves_gateway.service import IntegerConverterService


class IntegerConverterServiceSpec(unittest.TestCase):
    @patch.multiple(  # type: ignore
        IntegerConverterService, __abstractmethods__=set())
    def setUp(self):
        self._integer_converter = IntegerConverterService()

    def test_revert_amount_conversion(self):
        res = self._integer_converter.revert_amount_conversion(40)
        self.assertEqual(res, 40)

    def test_convert_amount_to_int(self):
        res = self._integer_converter.convert_amount_to_int(40.33)
        self.assertEqual(res, 40.33)

    def test_safely_convert_to_int_success(self):

        with patch.object(self._integer_converter, 'convert_amount_to_int'):
            self._integer_converter.convert_amount_to_int.return_value = 40
            res = self._integer_converter.safely_convert_to_int(0.40)
            self.assertEqual(res, 40)

    def test_safely_convert_to_int_throws(self):

        with patch.object(self._integer_converter, 'convert_amount_to_int'):
            self._integer_converter.convert_amount_to_int.return_value = 0.40
            with self.assertRaises(TypeError):
                self._integer_converter.safely_convert_to_int(0.40)

    def test_convert_transaction_to_int(self):
        transaction = Transaction(
            tx="79283647",
            receivers=[
                TransactionReceiver(address="9782364", amount=0.40),
                TransactionReceiver(address="9782364", amount=0.30)
            ])

        expected_result = Transaction(
            tx="79283647",
            receivers=[
                TransactionReceiver(address="9782364", amount=40),
                TransactionReceiver(address="9782364", amount=30)
            ])

        with patch.object(self._integer_converter, 'safely_convert_to_int'):

            def stub(amount: float):
                return int(amount * 100)

            self._integer_converter.safely_convert_to_int.side_effect = stub

            actual_result = self._integer_converter.convert_transaction_to_int(transaction)
            self.assertEqual(actual_result, expected_result)
            self.assertEqual(self._integer_converter.safely_convert_to_int.call_count, 2)

    def test_revert_transaction_conversion(self):
        expected_result = Transaction(
            tx="79283647",
            receivers=[
                TransactionReceiver(address="9782364", amount=0.40),
                TransactionReceiver(address="9782364", amount=0.30)
            ])

        transaction = Transaction(
            tx="79283647",
            receivers=[
                TransactionReceiver(address="9782364", amount=40),
                TransactionReceiver(address="9782364", amount=30)
            ])

        with patch.object(self._integer_converter, 'revert_amount_conversion'):

            def stub(amount: float):
                return float(amount / 100)

            self._integer_converter.revert_amount_conversion.side_effect = stub

            actual_result = self._integer_converter.revert_transaction_conversion(transaction)
            self.assertEqual(actual_result, expected_result)
