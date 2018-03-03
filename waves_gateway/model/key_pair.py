"""
KeyPair
"""

from typing import Any


class KeyPair(object):
    """
    Pair of a public and private element.
    """
    DICT_PUBLIC_KEY = 'public'
    DICT_SECRET_KEY = 'secret'

    def __init__(self, public: str, secret: str) -> None:
        """

        :param public: The public part is not required to be protected
        :param secret: The secret part must not be leaked
        """
        self._public = public
        self._secret = secret

    @property
    def public(self) -> str:
        return self._public

    @property
    def secret(self) -> str:
        return self._secret

    def __eq__(self, other: Any):
        """
        Compares two KeyPairs for equality.
        """
        if not isinstance(other, KeyPair):
            return False
        else:
            return other.secret == self.secret and other.public == self.public
