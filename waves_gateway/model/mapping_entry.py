"""
MappingEntry
"""


class MappingEntry(object):
    """
    Defines what will be saved in the MapStorage.
    A MappingEntry represents a connection between a custom currency address and a Waves address.
    """

    DICT_COIN_KEY = 'coin'
    DICT_WAVES_KEY = 'waves'

    def __init__(self, waves_address: str, coin_address: str) -> None:
        self._waves_address = waves_address
        self._coin_address = coin_address

    @property
    def waves_address(self) -> str:
        return self._waves_address

    @property
    def coin_address(self) -> str:
        return self._coin_address

    def __str__(self):
        return "Coin(" + str(self._coin_address) + ")" + " -> " + "Waves(" + str(self._waves_address) + ")"

    def __eq__(self, other):
        return self.waves_address == other.waves_address and self.coin_address == other.coin_address
