"""
CoinBlockHeightStorageProxyImpl
"""

from typing import Optional
from doc_inherit import method_doc_inherit  # type: ignore

from waves_gateway.common import Injectable
from waves_gateway.storage.key_value_storage import KeyValueStorage
from waves_gateway.storage.block_height_storage_proxy import BlockHeightStorageProxy


@Injectable(deps=[KeyValueStorage])
class CoinBlockHeightStorageProxyImpl(BlockHeightStorageProxy):
    """
    Forwards requests for the block height to the custom currency block height.
    """

    def __init__(self, key_value_storage: KeyValueStorage) -> None:
        self._key_value_storage = key_value_storage

    @method_doc_inherit
    def set_last_checked_block_height(self, block_height: int) -> None:
        return self._key_value_storage.set_last_checked_coin_block_height(block_height)

    @method_doc_inherit
    def get_last_checked_block_height(self) -> Optional[int]:
        """
        Returns the last checked block height of the custom currency.
        """
        return self._key_value_storage.get_last_checked_coin_block_height()
