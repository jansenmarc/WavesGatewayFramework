"""
SecretService
"""

import pywaves  # type: ignore

from waves_gateway.common import Injectable, GATEWAY_COIN_ADDRESS_SECRET, GATEWAY_PYWAVES_ADDRESS
from waves_gateway.storage import WalletStorage
from waves_gateway.model import KeyPair


@Injectable(deps=[WalletStorage, GATEWAY_COIN_ADDRESS_SECRET, GATEWAY_PYWAVES_ADDRESS])
class SecretService(object):
    """
    Forwards to the specific secret if any.
    Can be used to query any secret that the Gateway stores.
    """

    def __init__(self, wallet_storage: WalletStorage, gateway_coin_address_secret: KeyPair,
                 gateway_pywaves_address: pywaves.Address) -> None:
        self._wallet_storage = wallet_storage
        self._coin_gateway_address_secret = gateway_coin_address_secret
        self._gateway_pywaves_address = gateway_pywaves_address

    def get_secret_by_address(self, currency: str, address: str):
        if currency == "waves" and self._gateway_pywaves_address.address == address:
            return self._gateway_pywaves_address.privateKey
        elif currency == "coin":
            if self._coin_gateway_address_secret.public == address:
                return self._coin_gateway_address_secret.secret
            else:
                key_pair = self._wallet_storage.get_secret_by_public_address(address)
                if key_pair is not None:
                    return key_pair.secret
        return None
