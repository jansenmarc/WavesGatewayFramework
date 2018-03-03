"""
MappingEntrySerializer
"""
from waves_gateway.common import Injectable
from waves_gateway.model import MappingEntry


@Injectable()
class MappingEntrySerializer(object):
    """
    Defines how a MappingEntry can be serialized and deserialized.
    """

    # noinspection PyMethodMayBeStatic
    def as_dict(self, entry: MappingEntry) -> dict:
        """
        Converts a mapping entry into a dictionary containing all attributes.
        """
        res = dict()

        res[MappingEntry.DICT_WAVES_KEY] = entry.waves_address
        res[MappingEntry.DICT_COIN_KEY] = entry.coin_address

        return res
