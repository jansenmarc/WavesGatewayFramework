"""GatewayConfigFile"""

from typing import Optional, Union
from decimal import Decimal
from .key_pair import KeyPair


class GatewayConfigFile(object):
    """
    Contains the information of a parsed configuration file.
    """

    def __init__(self):
        self.waves_node = None  # type: Optional[str]
        self.coin_node = None  # type: Optional[str]
        self.coin_fee = None  # type: Optional[Union[int, Decimal]]
        self.gateway_fee = None  # type: Optional[Union[int, Decimal]]
        self.gateway_owner_address = None  # type: Optional[str]
        self.gateway_waves_address_secret = None  # type: Optional[KeyPair]
        self.gateway_coin_address_secret = None  # type: Optional[KeyPair]
        self.mongo_host = None  # type: Optional[str]
        self.mongo_port = None  # type: Optional[int]
        self.mongo_database = None  # type: Optional[str]
        self.waves_chain = None  # type: Optional[str]
        self.environment = None  # type: Optional[str]
        self.gateway_host = None  # type: Optional[str]
        self.gateway_port = None  # type: Optional[int]
        self.waves_chain_id = None  # type: Optional[str]
