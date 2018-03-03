"""
KeyPairSerializer
"""

from waves_gateway.common import ParseError, Injectable
from waves_gateway.model import KeyPair


@Injectable()
class KeyPairSerializer(object):
    """
    Can be used to serialize and deserialize a KeyPair derived alias such as an
    AccountSecret instance or an AddressSecret.
    """

    # noinspection PyMethodMayBeStatic
    def as_dict(self, key_pair: KeyPair) -> dict:
        """
        Transforms a KeyPair into a dictionary that contains all attributes of the KeyPair.
        After that, the dict may be persisted and deserialized later.
        For example, the dict representation may be converted into JSON using the standard json library.
        """
        res = dict()

        res[KeyPair.DICT_PUBLIC_KEY] = key_pair.public
        res[KeyPair.DICT_SECRET_KEY] = key_pair.secret

        return res

    # noinspection PyMethodMayBeStatic
    def from_dict(self, data: dict) -> KeyPair:
        """
        Tries to reconstruct a KeyPair from the given dictionary.
        This may fail if the dictionary does not define the necessary properties.
        In this case a ParseError is thrown.
        """

        if KeyPair.DICT_PUBLIC_KEY not in data:
            raise ParseError("required key '" + KeyPair.DICT_PUBLIC_KEY + "' is missing")

        if KeyPair.DICT_SECRET_KEY not in data:
            raise ParseError("required key '" + KeyPair.DICT_SECRET_KEY + "' is missing")

        return KeyPair(public=data[KeyPair.DICT_PUBLIC_KEY], secret=data[KeyPair.DICT_SECRET_KEY])
