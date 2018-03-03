"""
PublicConfiguration
"""

from typing import Optional


class PublicConfiguration:
    """
    Part of the configuration that is allowed to be available to the public,
    for example via ReST.
    """

    CUSTOM_CURRENCY_NAME_DICT_KEY = 'custom_currency_name'
    GATEWAY_WAVES_ADDRESS_DICT_KEY = 'gateway_waves_address'
    GATEWAY_COIN_HOLDER_DICT_KEY = 'gateway_coin_holder'
    WAVES_NODE_DICT_KEY = 'waves_node'
    WAVES_ASSET_ID = 'waves_asset_id'
    COIN_TRANSACTION_WEB_LINK = 'coin_transaction_web_link'
    WAVES_TRANSACTION_WEB_LINK = 'waves_transaction_web_link'
    COIN_ADDRESS_WEB_LINK = 'coin_address_web_link'
    WAVES_ADDRESS_WEB_LINK = 'waves_address_web_link'
    WEB_PRIMARY_COLOR = 'web_primary_color'

    def __init__(self,
                 custom_currency_name: str,
                 gateway_waves_address: str,
                 gateway_coin_address: str,
                 waves_node: str,
                 waves_asset_id: str,
                 waves_transaction_web_link: str,
                 waves_address_web_link: str,
                 coin_transaction_web_link: Optional[str] = None,
                 coin_address_web_link: Optional[str] = None,
                 web_primary_color: Optional[str] = None) -> None:
        self._custom_currency_name = custom_currency_name
        self._gateway_waves_address = gateway_waves_address
        self._gateway_coin_holder = gateway_coin_address
        self._waves_node = waves_node
        self._waves_asset_id = waves_asset_id
        self._coin_transaction_web_link = coin_transaction_web_link
        self._waves_transaction_web_link = waves_transaction_web_link
        self._waves_address_web_link = waves_address_web_link
        self._coin_address_web_link = coin_address_web_link
        self._web_primary_color = web_primary_color

    @property
    def custom_currency_name(self) -> str:
        return self._custom_currency_name

    @property
    def gateway_waves_address(self) -> str:
        return self._gateway_waves_address

    @property
    def gateway_coin_holder(self) -> str:
        return self._gateway_coin_holder

    @property
    def waves_node(self) -> str:
        return self._waves_node

    @property
    def waves_asset_id(self) -> str:
        return self._waves_asset_id

    @property
    def waves_transaction_web_link(self) -> str:
        return self._waves_transaction_web_link

    @property
    def coin_address_web_link(self) -> Optional[str]:
        return self._coin_address_web_link

    @property
    def coin_transaction_web_link(self) -> Optional[str]:
        return self._coin_transaction_web_link

    @property
    def waves_address_web_link(self) -> str:
        return self._waves_address_web_link

    @property
    def web_primary_color(self) -> str:
        return self._web_primary_color
