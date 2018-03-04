import unittest

import math

from decimal import Decimal
from waves_gateway.common.utils import convert_to_int, convert_to_decimal


class UtilsSpec(unittest.TestCase):
    def test_convert_float_to_int(self):
        value = float(8.04)
        factor = math.pow(10, 2)
        self.assertEqual(convert_to_int(value, factor), 804)

    def test_convert_decimal_to_int(self):
        value = Decimal(8.0492)
        factor = pow(10, 4)
        self.assertEqual(convert_to_int(value, factor), 80492)

    def test_convert_to_decimal_with_precision(self):
        value = 78888
        factor = math.pow(10, 2)
        res = convert_to_decimal(value, factor, 1)
        self.assertIsInstance(res, Decimal)
        self.assertEqual(res, round(Decimal(788.9), 1))
