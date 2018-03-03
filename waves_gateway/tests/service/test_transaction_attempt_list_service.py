import unittest
from typing import cast
from unittest.mock import MagicMock, patch
import datetime
import logging

from waves_gateway import TransactionService, TransactionAttempt, TransactionAttemptReceiver, Transaction, \
    TransactionReceiver
from waves_gateway.model import TransactionAttemptList, AttemptListTrigger, TransactionSender
from waves_gateway.service import TransactionAttemptListService, SecretService
from waves_gateway.storage import TransactionAttemptListStorage


class TransactionAttemptListServiceSpec(unittest.TestCase):
    def setUp(self):
        self._transaction_service = MagicMock()
        self._secret_service = MagicMock()
        self._logger = MagicMock()
        self._storage = MagicMock()

        self._attempt_list_service = TransactionAttemptListService(
            logger=cast(logging.Logger, self._logger),
            secret_service=cast(SecretService, self._secret_service),
            transaction_attempt_list_storage=cast(TransactionAttemptListStorage, self._storage),
            transaction_service=cast(TransactionService, self._transaction_service))

    @patch('datetime.datetime', autospec=True)
    def test_continue_transaction_attempt_list(self, mock_datetime: MagicMock):
        now = MagicMock()
        mock_datetime.utcnow.return_value = now

        trigger = AttemptListTrigger(
            tx="792873", receiver=1, currency="waves", senders=[TransactionSender(address="723789")])

        attempt_list = TransactionAttemptList(
            trigger=trigger,
            attempts=[
                TransactionAttempt(
                    currency="coin",
                    fee=100,
                    receivers=[TransactionAttemptReceiver(address="973846", amount=234)],
                    sender="739264857")
            ],
            created_at=now,
            last_modified=now)

        expected_attempt_list = TransactionAttemptList(
            trigger=trigger,
            attempts=[
                TransactionAttempt(
                    currency="coin",
                    fee=100,
                    receivers=[TransactionAttemptReceiver(address="973846", amount=234)],
                    sender="739264857"),
            ],
            transactions=["97238"],
            created_at=now,
            last_modified=now)

        mock_transaction = Transaction(tx="97238", receivers=[TransactionReceiver(address="973846", amount=234)])

        mock_secret = "9723684"

        self._secret_service.get_secret_by_address.return_value = mock_secret
        self._transaction_service.send_coin.return_value = mock_transaction

        self._attempt_list_service.continue_transaction_attempt_list(attempt_list)

        self._storage.update_attempt_list.assert_called_once_with(expected_attempt_list)
        self._transaction_service.send_coin.assert_called_once_with(attempt_list.attempts[0], mock_secret)
        self._secret_service.get_secret_by_address("coin", "739264857")
