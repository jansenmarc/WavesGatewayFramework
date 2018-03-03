import unittest
from unittest.mock import MagicMock

from waves_gateway import ProxyGuard


class ProxyGuardTest(unittest.TestCase):
    def test_method_call(self):
        mock_proxy = MagicMock()
        mock_result = MagicMock()

        mock_args = [MagicMock(), MagicMock()]

        mock_proxy.mock_func.return_value = mock_result

        proxy_guard = ProxyGuard(mock_proxy)

        res = proxy_guard.mock_func(mock_args[0], mock_args[1])

        self.assertEqual(res, mock_result)
        mock_proxy.mock_func.assert_called_once_with(mock_args[0], mock_args[1])

    def test_method_call_with_exception(self):
        mock_proxy = MagicMock()

        mock_args = [MagicMock(), MagicMock()]

        def mock_func(arg1, arg2):
            raise KeyError()

        mock_proxy.mock_func.side_effect = mock_func

        proxy_guard = ProxyGuard(mock_proxy)

        with self.assertRaises(KeyError):
            proxy_guard.mock_func(mock_args[0], mock_args[1])

        mock_proxy.mock_func.assert_called_once_with(mock_args[0], mock_args[1])
