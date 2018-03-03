"""
FeeServiceConverterProxyImpl
"""
from waves_gateway.common import Injectable
from waves_gateway.service.token import COIN_INTEGER_CONVERTER_SERVICE

from .fee_service import FeeService
from .integer_converter_service import IntegerConverterService


@Injectable(deps=[FeeService, COIN_INTEGER_CONVERTER_SERVICE])
class FeeServiceConverterProxyImpl(FeeService):
    """
    Converts the results of the FeeService to int values that can be further processed by the Gateway.
    """

    def __init__(self, fee_service: FeeService, coin_integer_converter_service: IntegerConverterService) -> None:
        self._fee_service = fee_service
        self._coin_converter_service = coin_integer_converter_service

    def get_gateway_fee(self) -> int:
        return self._coin_converter_service.safely_convert_to_int(self._fee_service.get_gateway_fee())

    def get_coin_fee(self) -> int:
        return self._coin_converter_service.safely_convert_to_int(self._fee_service.get_coin_fee())

    def get_waves_fee(self) -> int:
        return self._fee_service.get_waves_fee()
