import unittest

from waves_gateway.model import KeyPair
from waves_gateway.serializer import KeyPairSerializer


class KeyPairSerializerSpec(unittest.TestCase):
    def setUp(self):
        self._serializer = KeyPairSerializer()

    def test_serialize(self):
        secret = KeyPair('public', 'secret')
        serialized = self._serializer.as_dict(secret)
        self.assertIsInstance(serialized, dict)
        unserialized = self._serializer.from_dict(serialized)
        self.assertIsInstance(unserialized, KeyPair)
        self.assertEqual(secret, unserialized)
