"""
GatewayControllerConverterProxyImpl
"""

from typing import Optional, List
from waves_gateway.common import map_array, Injectable
from waves_gateway.service import AttemptListConverterService

from waves_gateway.model import AttemptListTrigger, TransactionAttemptList, AttemptListQuery

from .gateway_controller import GatewayController


@Injectable(deps=[AttemptListConverterService, GatewayController])
class GatewayControllerConverterProxyImpl(GatewayController):
    """
    Reverts the amount conversion which the Gateway internally uses before overhanding the results
    to an external API.
    """

    def check_coin_transaction(self, tx: str) -> None:
        self._gateway_controller.check_coin_transaction(tx)

    def check_waves_transaction(self, tx: str) -> None:
        self._gateway_controller.check_waves_transaction(tx)

    def validate_waves_address(self, address: str) -> bool:
        return self._gateway_controller.validate_waves_address(address)

    def query_attempt_lists(self, query: AttemptListQuery) -> List[TransactionAttemptList]:
        results = self._gateway_controller.query_attempt_lists(query)
        return map_array(lambda x: self._converter.revert_attempt_list_conversion(x), results)

    def get_attempt_list_by_id(self, attempt_list_id: str) -> Optional[TransactionAttemptList]:
        result = self._gateway_controller.get_attempt_list_by_id(attempt_list_id)
        if result is None:
            return None
        else:
            return self._converter.revert_attempt_list_conversion(result)

    def get_average_attempt_list_tries(self):
        return self._gateway_controller.get_average_attempt_list_tries()

    def __init__(self, attempt_list_converter_service: AttemptListConverterService,
                 gateway_controller: GatewayController) -> None:
        self._converter = attempt_list_converter_service
        self._gateway_controller = gateway_controller

    def get_attempt_list_by_trigger(self, trigger: AttemptListTrigger) -> Optional[TransactionAttemptList]:
        return self._converter.revert_attempt_list_conversion(
            self._gateway_controller.get_attempt_list_by_trigger(trigger))

    def get_failed_transactions(self):
        return self._gateway_controller.get_failed_transactions()

    def get_block_heights(self):
        return self._gateway_controller.get_block_heights()

    def get_log_messages(self):
        return self._gateway_controller.get_log_messages()

    def create_address(self, waves_address: str) -> str:
        return self._gateway_controller.create_address(waves_address)

    def trigger_attemptlist_retry(self, id: str) -> str:
        return self._gateway_controller.trigger_attemptlist_retry(id)
