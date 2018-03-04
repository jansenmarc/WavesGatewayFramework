from unittest import TestCase
from unittest.mock import MagicMock, patch, ANY
from waves_gateway.service import GatewayApplicationService


class TestGatewayApplicationService(TestCase):
    def setUp(self):
        self._validation_service = MagicMock()
        self._logger = MagicMock()
        self._coin_transaction_polling_service = MagicMock()
        self._waves_transaction_polling_service = MagicMock()
        self._num_attempt_list_workers = 3
        self._attempt_list_service = MagicMock()
        self._attempt_list_selector = MagicMock()
        self._polling_delay_config = MagicMock()
        self._flask = MagicMock()
        self._host = 'test_host'
        self._port = 23512

        self._application = GatewayApplicationService(
            validation_service=self._validation_service,
            logger=self._logger,
            coin_transaction_polling_service=self._coin_transaction_polling_service,
            waves_transaction_polling_service=self._waves_transaction_polling_service,
            num_attempt_list_workers=self._num_attempt_list_workers,
            attempt_list_service=self._attempt_list_service,
            attempt_list_selector=self._attempt_list_selector,
            polling_delay_config=self._polling_delay_config,
            flask=self._flask,
            host=self._host,
            port=self._port)

    @patch('gevent.pywsgi.WSGIServer', autospec=True)
    @patch('gevent.pool.Group', autospec=True)
    @patch('gevent.signal', autospec=True)
    def test_run(self, signal: MagicMock, group_clazz: MagicMock, wsgi_server_clazz: MagicMock):

        group_instance = MagicMock()
        group_clazz.return_value = group_instance

        wsgi_server_instance = MagicMock()
        wsgi_server_clazz.return_value = wsgi_server_instance

        with patch.object(self._application, "_create_attempt_list_workers"):
            self._application._create_attempt_list_workers.return_value = []
            self._application.run()

        group_instance.start.assert_any_call(self._waves_transaction_polling_service)
        group_instance.start.assert_any_call(self._coin_transaction_polling_service)
        group_clazz.assert_called_once_with()
        wsgi_server_clazz.assert_called_once_with((self._host, self._port), self._flask, log=ANY)
        wsgi_server_instance.serve_forever.assert_called_once_with()
