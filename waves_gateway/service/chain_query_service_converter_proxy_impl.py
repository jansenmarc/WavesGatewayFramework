"""
ChainQueryServiceConverterProxyImpl
"""

from typing import List, Optional

from waves_gateway.common import map_array, Injectable, COIN_CHAIN_QUERY_SERVICE_CONVERTER_PROXY, \
    WAVES_CHAIN_QUERY_SERVICE_CONVERTER_PROXY
from waves_gateway.model import Transaction

from .chain_query_service import ChainQueryService
from .integer_converter_service import IntegerConverterService
from .token import COIN_CHAIN_QUERY_SERVICE, COIN_INTEGER_CONVERTER_SERVICE, ASSET_INTEGER_CONVERTER_SERVICE, WAVES_CHAIN_QUERY_SERVICE


@Injectable(COIN_CHAIN_QUERY_SERVICE_CONVERTER_PROXY, deps=[COIN_CHAIN_QUERY_SERVICE, COIN_INTEGER_CONVERTER_SERVICE])
@Injectable(
    WAVES_CHAIN_QUERY_SERVICE_CONVERTER_PROXY, deps=[WAVES_CHAIN_QUERY_SERVICE, ASSET_INTEGER_CONVERTER_SERVICE])
class ChainQueryServiceConverterProxyImpl(ChainQueryService):
    """
    Applies the given IntegerConverterService on the result of the given ChainQueryService.
    """

    def get_transaction_by_tx(self, tx: str) -> Optional[Transaction]:
        transaction = self._chain_query_service.get_transaction_by_tx(tx)

        if transaction is not None:
            return self._integer_converter_service.convert_transaction_to_int(transaction)
        else:
            return None

    def __init__(self, chain_query_service: ChainQueryService,
                 integer_converter_service: IntegerConverterService) -> None:
        self._integer_converter_service = integer_converter_service
        self._chain_query_service = chain_query_service

    def get_transactions_of_block_at_height(self, height: int) -> List[Transaction]:
        transactions = self._chain_query_service.get_transactions_of_block_at_height(height)
        return map_array(lambda x: self._integer_converter_service.convert_transaction_to_int(x), transactions)

    def get_height_of_highest_block(self) -> int:
        return self._chain_query_service.get_height_of_highest_block()

    def get_coin_receiver_address_from_transaction(self, transaction: str):
        return self._chain_query_service.get_coin_receiver_address_from_transaction(transaction)
