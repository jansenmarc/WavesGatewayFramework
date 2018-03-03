"""
TransactionAttemptListService
"""

import logging

from waves_gateway.common import Injectable
from .transaction_service_forwarder_proxy_impl import TransactionServiceForwarderProxyImpl

from .secret_service import SecretService
from waves_gateway.storage import TransactionAttemptListStorage
from .transaction_service import TransactionService
from waves_gateway.model import TransactionAttemptList, TransactionAttempt


@Injectable(deps=[TransactionServiceForwarderProxyImpl, SecretService, logging.Logger, TransactionAttemptListStorage])
class TransactionAttemptListService(object):
    """
    Defines how to process a TransactionAttemptList.
    """

    def __init__(self, transaction_service: TransactionService, secret_service: SecretService, logger: logging.Logger,
                 transaction_attempt_list_storage: TransactionAttemptListStorage) -> None:
        self._transaction_service = transaction_service
        self._secret_service = secret_service
        self._logger = logger.getChild(self.__class__.__name__)
        self._storage = transaction_attempt_list_storage

    def continue_transaction_attempt_list(self, attempt_list: TransactionAttemptList) -> None:
        self._logger.info("Trying to complete attempt_list '%s'", attempt_list.attempt_list_id)

        if attempt_list.is_complete():
            self._logger.info("attempt_list is already complete")
            return

        for i in range(0, len(attempt_list.transactions)):
            self._log_attempt_alredy_done(attempt_list.attempts[i])

        while not attempt_list.is_complete():
            next_attempt = attempt_list.next_incomplete_attempt()
            transaction = self._transaction_service.send_coin(next_attempt,
                                                              self._secret_service.get_secret_by_address(
                                                                  next_attempt.currency, next_attempt.sender))
            attempt_list.mark_next_attempt_as_complete(next_attempt, transaction.tx)
            self._storage.update_attempt_list(attempt_list)
            self._log_attempt_success(next_attempt)

        self._logger.info("attempt_list '%s' is complete", attempt_list.attempt_list_id)

    def _log_attempt_success(self, attempt: TransactionAttempt):
        for receiver in attempt.receivers:
            self._logger.info("[%s]: Transferred %s from %s to %s", str(attempt.currency), str(receiver.amount),
                              str(attempt.sender), str(receiver.address))

    def _log_attempt_alredy_done(self, attempt: TransactionAttempt):
        for receiver in attempt.receivers:
            self._logger.info("[%s]: Already transferred %s from %s to %s", str(attempt.currency), str(receiver.amount),
                              str(attempt.sender), str(receiver.address))
