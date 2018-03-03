"""
MongoMapStorageImpl
"""

from typing import Optional

from doc_inherit import method_doc_inherit  # type: ignore
from pymongo.collection import Collection  # type: ignore

from waves_gateway.common import Injectable, MAP_STORAGE_COLLECTION
from waves_gateway.model import MappingEntry
from waves_gateway.serializer import MappingEntrySerializer
from .map_storage import MapStorage


@Injectable(deps=[MAP_STORAGE_COLLECTION, MappingEntrySerializer], provides=MapStorage)
class MongoMapStorageImpl(MapStorage):
    """
    Implementation of a MapStorage using a MongoDB.
    """

    @method_doc_inherit
    def save_mapping(self, mapping: MappingEntry):
        self._collection.insert_one(self._serializer.as_dict(mapping))

    def __init__(self, collection: Collection, serializer: MappingEntrySerializer) -> None:
        super().__init__()
        self._collection = collection
        self._serializer = serializer

    @method_doc_inherit
    def get_waves_address_by_coin_address(self, coin_address: str) -> Optional[str]:
        query = dict()
        query[MappingEntry.DICT_COIN_KEY] = coin_address

        query_result = self._collection.find_one(query)
        if query_result is None:
            return None
        else:
            return str(query_result[MappingEntry.DICT_WAVES_KEY])

    @method_doc_inherit
    def get_coin_address_by_waves_address(self, waves_address: str) -> Optional[str]:
        query = dict()
        query[MappingEntry.DICT_WAVES_KEY] = waves_address
        query_result = self._collection.find_one(query)
        if query_result is None:
            return None
        else:
            return str(query_result[MappingEntry.DICT_COIN_KEY])
