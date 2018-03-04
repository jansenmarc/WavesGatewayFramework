import unittest

from waves_gateway import ConstantFeeServiceImpl


class ConstantFeeServiceImplTest(unittest.TestCase):
    def setUp(self):
        self._gateway_fee = 2735
        self._coin_fee = 2423
        self._waves_fee = 243

        self._fee_service = ConstantFeeServiceImpl(
            gateway_fee=self._gateway_fee, coin_fee=self._coin_fee, waves_fee=self._waves_fee)

    def test_get_gateway_fee(self):
        self.assertEqual(self._fee_service.get_gateway_fee(), self._gateway_fee)

    def test_get_coin_fee(self):
        self.assertEqual(self._fee_service.get_coin_fee(), self._coin_fee)

    def test_get_waves_fee(self):
        self.assertEqual(self._fee_service.get_waves_fee(), self._waves_fee)
