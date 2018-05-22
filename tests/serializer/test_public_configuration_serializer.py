import unittest

from waves_gateway.model import PublicConfiguration

from waves_gateway.serializer import PublicConfigurationSerializer


class PublicConfigurationSerializerSpec(unittest.TestCase):
    def setUp(self):
        self._serializer = PublicConfigurationSerializer()

    def test_as_dict(self):
        config = PublicConfiguration(
            base_currecy_name="Turtle Network",
            custom_currency_name="Litecoin",
            gateway_coin_address="9652973",
            gateway_waves_address="2798273189",
            waves_address_web_link="http://waves_address@test.com",
            coin_transaction_web_link="http://coin_transaction@test.com",
            waves_asset_id="017283958902359",
            waves_node="http://325.213.123",
            waves_transaction_web_link="http://waves_transaction@test.com")

        res = self._serializer.as_dict(config)

        self.assertFalse(PublicConfiguration.COIN_ADDRESS_WEB_LINK in res)
        self.assertEqual(res[PublicConfiguration.WAVES_ADDRESS_WEB_LINK], config.waves_address_web_link)
        self.assertEqual(res[PublicConfiguration.COIN_TRANSACTION_WEB_LINK], config.coin_transaction_web_link)
        self.assertEqual(res[PublicConfiguration.WAVES_TRANSACTION_WEB_LINK], config.waves_transaction_web_link)
        self.assertEqual(res[PublicConfiguration.CUSTOM_CURRENCY_NAME_DICT_KEY], config.custom_currency_name)
        self.assertEqual(res[PublicConfiguration.BASE_CURRENCY_NAME_DICT_KEY], config.base_currency_name)
        self.assertEqual(res[PublicConfiguration.GATEWAY_COIN_HOLDER_DICT_KEY], config.gateway_coin_holder)
        self.assertEqual(res[PublicConfiguration.GATEWAY_WAVES_ADDRESS_DICT_KEY], config.gateway_waves_address)
        self.assertEqual(res[PublicConfiguration.WAVES_ASSET_ID], config.waves_asset_id)
        self.assertEqual(res[PublicConfiguration.WAVES_NODE_DICT_KEY], config.waves_node)
