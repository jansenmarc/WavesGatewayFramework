from unittest import TestCase

from decimal import Decimal

from waves_gateway.common import InvalidConfigError
from waves_gateway.model import KeyPair

from waves_gateway.service import GatewayConfigParser


class GatewayConfigParserTest(TestCase):
    def setUp(self):
        self._parser = GatewayConfigParser()

    def test_parse_config_file_content(self):
        config_file = """
            [node]
            coin = http://bla:test@345.234.23.234:20000
            waves = http://342.234.234.253:6869

            [fee]
            coin = 0.02000000
            gateway = 0.01000000

            [gateway_address]
            owner = akgsjfhsjkghweg
            waves_public_key = hjskgfj234786hfjk
            waves_private_key = 698473256icz7zftj
            coin_public_key = cgi34zvci7

            [mongodb]
            host = localhost
            port = 27017
            database = ltc-gateway

            [other]
            environment = test
            waves_chain = testnet
            [api]
            key = 1234567890
        """

        parsed = self._parser.parse_config_file_content(config_file)

        # --- [node] ---
        self.assertEqual(parsed.coin_node, "http://bla:test@345.234.23.234:20000")
        self.assertEqual(parsed.waves_node, "http://342.234.234.253:6869")

        # --- [fee] ---
        self.assertEqual(parsed.coin_fee, Decimal("0.02"))
        self.assertEqual(parsed.gateway_fee, Decimal("0.01"))

        # --- [gateway_address] ---
        self.assertEqual(parsed.gateway_owner_address, "akgsjfhsjkghweg")
        self.assertEqual(parsed.gateway_waves_address_secret,
                         KeyPair(public="hjskgfj234786hfjk", secret="698473256icz7zftj"))
        self.assertEqual(parsed.gateway_coin_address_secret, KeyPair(public="cgi34zvci7", secret=None))

        # --- [mongodb] ---
        self.assertEqual(parsed.mongo_host, "localhost")
        self.assertEqual(parsed.mongo_port, 27017)
        self.assertEqual(parsed.mongo_database, "ltc-gateway")

        # --- [other] ---
        self.assertEqual(parsed.environment, "test")
        self.assertEqual(parsed.waves_chain, "testnet")
        self.assertEqual(parsed.gateway_api_key, "1234567890")

    def test_using_old_ltc_should_fail(self):
        config_file = """
            [node]
            coin = http://bla:test@345.234.23.234:20000
            waves = http://342.234.234.253:6869

            [fee]
            ltc = 0.02000000
            gateway = 0.01000000

            [gateway_address]
            owner = akgsjfhsjkghweg
            waves_public_key = hjskgfj234786hfjk
            waves_private_key = 698473256icz7zftj
            coin_public_key = cgi34zvci7

            [mongodb]
            host = localhost
            port = 27017
            database = ltc-gateway

            [other]
            environment = test
            waves_chain = testnet
        """

        with self.assertRaises(InvalidConfigError):
            self._parser.parse_config_file_content(config_file)
