"""
GatewayApplicationService
"""

from logging import Logger

import signal
from typing import List

import flask
import gevent
import gevent.pywsgi
import gevent.pool

from waves_gateway.model import PollingDelayConfig
from waves_gateway.common import Injectable, NUM_ATTEMPT_LIST_WORKERS, GATEWAY_HOST, GATEWAY_PORT
from .gateway_validation_service import GatewayValidationService
from .transaction_polling_service import TransactionPollingService
from .attempt_list_worker import AttemptListWorker
from .transaction_attempt_list_service import TransactionAttemptListService
from .pending_attempt_list_selector_service import PendingAttemptListSelectorService
from .token import COIN_TRANSACTION_POLLING_SERVICE, WAVES_TRANSACTION_POLLING_SERVICE


@Injectable(deps=[
    GatewayValidationService, Logger, COIN_TRANSACTION_POLLING_SERVICE, WAVES_TRANSACTION_POLLING_SERVICE,
    NUM_ATTEMPT_LIST_WORKERS, TransactionAttemptListService, PendingAttemptListSelectorService, PollingDelayConfig,
    flask.Flask, GATEWAY_HOST, GATEWAY_PORT
])
class GatewayApplicationService(object):
    """
    Implements the run method of the Gateway. This functionality was moved from the main Gateway class to here
    to simplify the main Gateway class. The run method starts all pollers.
    """

    def __init__(self, validation_service: GatewayValidationService, logger: Logger,
                 coin_transaction_polling_service: TransactionPollingService,
                 waves_transaction_polling_service: TransactionPollingService, num_attempt_list_workers: int,
                 attempt_list_service: TransactionAttemptListService,
                 attempt_list_selector: PendingAttemptListSelectorService, polling_delay_config: PollingDelayConfig,
                 flask: flask.Flask, host: str, port: int) -> None:
        self._validation_service = validation_service
        self._logger = logger.getChild(GatewayApplicationService.__name__)
        self._coin_transaction_polling_service = coin_transaction_polling_service
        self._waves_transaction_polling_service = waves_transaction_polling_service
        self._num_attempt_list_workers = num_attempt_list_workers
        self._attempt_list_service = attempt_list_service
        self._attempt_list_selector = attempt_list_selector
        self._polling_delay_config = polling_delay_config
        self._host = host
        self._port = port
        self._flask = flask

    def _create_attempt_list_workers(self) -> List[AttemptListWorker]:
        tasks = list()  # type: List[AttemptListWorker]

        for i in range(0, self._num_attempt_list_workers):
            task = AttemptListWorker(
                attempt_list_service=self._attempt_list_service,
                attempt_list_selector=self._attempt_list_selector,
                logger=self._logger,
                worker_id=i,
                max_polling_delay_s=self._polling_delay_config.attempt_list_worker_max_polling_delay_s,
                min_polling_delay_s=self._polling_delay_config.attempt_list_worker_min_polling_delay_s)

            tasks.append(task)

        return tasks

    def run(self) -> None:
        """
        Starts all poller instances.
        After that, polling is performed in regular intervals specified by the polling_delay_ms property.
        By default this function blocks the current thread.
        """
        self._validation_service.validate_all_addresses()

        self._logger.info("Gateway Application started")

        task_group = gevent.pool.Group()

        gevent.signal(signal.SIGINT, self._coin_transaction_polling_service.cancel)
        gevent.signal(signal.SIGINT, self._waves_transaction_polling_service.cancel)

        task_group.start(self._coin_transaction_polling_service)
        task_group.start(self._waves_transaction_polling_service)

        attempt_list_workers = self._create_attempt_list_workers()

        for worker in attempt_list_workers:
            gevent.signal(signal.SIGINT, worker.cancel)
            task_group.start(worker)

        http = gevent.pywsgi.WSGIServer(
            (self._host, self._port), self._flask, log=gevent.pywsgi.LoggingLogAdapter(self._logger.getChild('pywsgi')))

        gevent.signal(signal.SIGINT, http.close)

        self._logger.info('Listening on %s:%s', self._host, str(self._port))

        http.serve_forever()

        task_group.join(raise_error=True)
