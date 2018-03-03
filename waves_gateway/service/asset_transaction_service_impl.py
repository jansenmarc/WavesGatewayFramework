"""
AssetTransactionServiceImpl
"""

from typing import Optional

from waves_gateway.common import PyWavesError, Injectable, WAVES_ASSET_ID, GATEWAY_PYWAVES_ADDRESS
from waves_gateway.model import TransactionReceiver, TransactionAttempt, Transaction
from .transaction_service import TransactionService
import pywaves as pw  # type: ignore


@Injectable(deps=[WAVES_ASSET_ID, GATEWAY_PYWAVES_ADDRESS])
class AssetTransactionServiceImpl(TransactionService):
    """
    Implements a TransactionService that is capable of processing an TransactionAttempt instance
    with a 'waves' currency.
    """

    def __init__(self, waves_asset_id: str, gateway_pywaves_address: pw.Address) -> None:
        self._w_ltc = pw.Asset(waves_asset_id)
        self._gateway_pywaves_address = gateway_pywaves_address

    def send_coin(self, attempt: TransactionAttempt, secret: Optional[str]) -> Transaction:
        if attempt.sender != self._gateway_pywaves_address.address:
            raise PyWavesError('Missing secret for sender ' + attempt.sender)

        transaction = self._gateway_pywaves_address.sendAsset(
            recipient=pw.Address(attempt.receivers[0].address),
            asset=self._w_ltc,
            amount=attempt.receivers[0].amount,
            txFee=attempt.fee)

        if transaction is None:
            raise PyWavesError("Encountered an unknown exception while trying to perform waves transaction.")

        return Transaction(
            tx=transaction['id'],
            receivers=[TransactionReceiver(transaction['recipient'], attempt.receivers[0].amount)])
