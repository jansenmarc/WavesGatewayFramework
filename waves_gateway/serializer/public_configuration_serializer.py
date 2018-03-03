"""
PublicConfigurationSerializer
"""
from waves_gateway.common import Injectable
from waves_gateway.model import PublicConfiguration


@Injectable()
class PublicConfigurationSerializer(object):
    """
    Defines the conversion of a PublicConfiguration instance into a dict object.
    The resulting object may be delivered to the Web Application.
    """

    def as_dict(self, value: PublicConfiguration) -> dict:
        res = dict()

        res[PublicConfiguration.CUSTOM_CURRENCY_NAME_DICT_KEY] = value.custom_currency_name
        res[PublicConfiguration.GATEWAY_WAVES_ADDRESS_DICT_KEY] = value.gateway_waves_address
        res[PublicConfiguration.GATEWAY_COIN_HOLDER_DICT_KEY] = value.gateway_coin_holder
        res[PublicConfiguration.WAVES_NODE_DICT_KEY] = value.waves_node
        res[PublicConfiguration.WAVES_ASSET_ID] = value.waves_asset_id
        res[PublicConfiguration.WEB_PRIMARY_COLOR] = value.web_primary_color

        if value.coin_transaction_web_link is not None:
            res[PublicConfiguration.COIN_TRANSACTION_WEB_LINK] = value.coin_transaction_web_link

        if value.coin_address_web_link is not None:
            res[PublicConfiguration.COIN_ADDRESS_WEB_LINK] = value.coin_address_web_link

        res[PublicConfiguration.WAVES_ADDRESS_WEB_LINK] = value.waves_address_web_link
        res[PublicConfiguration.WAVES_TRANSACTION_WEB_LINK] = value.waves_transaction_web_link

        return res
