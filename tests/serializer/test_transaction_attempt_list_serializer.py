import unittest

from waves_gateway.model import AttemptListTrigger, TransactionSender, TransactionAttemptList, TransactionAttempt, \
    TransactionAttemptReceiver

from waves_gateway.serializer import TransactionAttemptListSerializer


class TransactionAttemptListSerializerSpec(unittest.TestCase):
    def setUp(self):
        self._attempt_list_serializer = TransactionAttemptListSerializer()

        trigger = AttemptListTrigger(
            tx="792873", receiver=1, currency="waves", senders=[TransactionSender(address="723789")])

        self._attempt_list = TransactionAttemptList(
            trigger=trigger,
            attempts=[
                TransactionAttempt(
                    currency="coin",
                    fee=100,
                    receivers=[
                        TransactionAttemptReceiver(address="973846", amount=234),
                        TransactionAttemptReceiver(address="9327468", amount=235)
                    ],
                    sender="739264857")
            ])

    def test_all(self):
        as_dict = self._attempt_list_serializer.attempt_list_as_dict(self._attempt_list)
        attempt_list = self._attempt_list_serializer.attempt_list_from_dict(as_dict)

        self.assertEqual(attempt_list, self._attempt_list)
