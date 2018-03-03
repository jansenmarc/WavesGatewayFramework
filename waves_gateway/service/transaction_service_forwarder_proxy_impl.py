"""
TransactionServiceForwarderProxyImpl
"""

from typing import Optional

from waves_gateway.common import Injectable
from waves_gateway.model import TransactionAttempt, Transaction
from .token import COIN_TRANSACTION_SERVICE_CONVERTER_PROXY, WAVES_TRANSACTION_SERVICE_CONVERTER_PROXY

from .transaction_service import TransactionService


@Injectable(deps=[COIN_TRANSACTION_SERVICE_CONVERTER_PROXY, WAVES_TRANSACTION_SERVICE_CONVERTER_PROXY])
class TransactionServiceForwarderProxyImpl(TransactionService):
    """
    Forwards the transaction attempt to the correct transaction_service based
    on the selected currency.
    """

    def __init__(self, coin_transaction_service: TransactionService,
                 asset_transaction_service: TransactionService) -> None:
        self._coin_transaction_service = coin_transaction_service
        self._asset_transaction_service = asset_transaction_service

    def send_coin(self, attempt: TransactionAttempt, secret: Optional[str]) -> Transaction:
        if attempt.currency == "waves":
            return self._asset_transaction_service.send_coin(attempt, secret)
        elif attempt.currency == "coin":
            return self._coin_transaction_service.send_coin(attempt, secret)
        else:
            raise Exception("Cannot handle currency " + attempt.currency)
