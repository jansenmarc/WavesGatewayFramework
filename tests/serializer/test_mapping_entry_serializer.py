import unittest

from waves_gateway.model import MappingEntry
from waves_gateway.serializer import MappingEntrySerializer


class MappingEntrySerializerSpec(unittest.TestCase):
    def setUp(self):
        self._serializer = MappingEntrySerializer()

    def test_serialize(self):
        entry = MappingEntry(coin_address='coin', waves_address='waves')
        serialized = self._serializer.as_dict(entry)

        self.assertIsInstance(serialized, dict)

        self.assertEqual(serialized[MappingEntry.DICT_COIN_KEY], 'coin')
        self.assertEqual(serialized[MappingEntry.DICT_WAVES_KEY], 'waves')
