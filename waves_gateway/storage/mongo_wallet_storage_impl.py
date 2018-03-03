"""
MongoWalletStorageImpl
"""

from typing import Optional

from pymongo.collection import Collection  # type: ignore
from doc_inherit import method_doc_inherit  # type: ignore

from waves_gateway.common import Injectable, WALLET_STORAGE_COLLECTION
from waves_gateway.model import KeyPair
from waves_gateway.serializer import KeyPairSerializer
from .wallet_storage import WalletStorage


@Injectable(deps=[WALLET_STORAGE_COLLECTION, KeyPairSerializer], provides=WalletStorage)
class MongoWalletStorageImpl(WalletStorage):
    """
    Wallet storage implementation using a MongoDB.
    """

    def __init__(self, collection: Collection, serializer: KeyPairSerializer) -> None:
        self._collection = collection
        self._serializer = serializer

    @method_doc_inherit
    def save_address_secret(self, secret: KeyPair) -> None:
        self._collection.insert_one(self._serializer.as_dict(secret))

    @method_doc_inherit
    def get_secret_by_public_address(self, public_address: str) -> Optional[KeyPair]:
        query = dict()
        query[KeyPair.DICT_PUBLIC_KEY] = public_address
        query_result = self._collection.find_one(query)

        if query_result is None:
            return None
        else:
            return self._serializer.from_dict(query_result)
