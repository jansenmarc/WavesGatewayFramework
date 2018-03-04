from unittest import TestCase
from unittest.mock import MagicMock

from waves_gateway.storage import CoinPollingStateStorageProxyImpl


class CoinPollingStateStorageProxyImplTest(TestCase):
    def setUp(self):
        self._key_value_storage = MagicMock()

        self._polling_state_storage = CoinPollingStateStorageProxyImpl(key_value_storage=self._key_value_storage)

    def test_set_polling_state(self):
        state = MagicMock()
        self._polling_state_storage.set_polling_state(state)
        self._key_value_storage.set_coin_polling_state.assert_called_once_with(state)

    def test_get_polling_state(self):
        state_result = MagicMock()
        self._key_value_storage.get_coin_polling_state.return_value = state_result
        self.assertIs(state_result, self._polling_state_storage.get_polling_state())
