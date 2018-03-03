"""
TransactionAttemptListSerializer
"""

from typing import Any, Union

from waves_gateway.model import TransactionAttemptList, TransactionAttempt, TransactionAttemptReceiver, \
    AttemptListTrigger, TransactionSender

from waves_gateway.common import map_array, Injectable


@Injectable()
class TransactionAttemptListSerializer(object):
    """
    Defines a conversion from an TransactionAttemptList instance into a dict instance
    and backwards. The dict instance can be used for persistence or an external API.
    """

    # noinspection PyMethodMayBeStatic
    def _receiver_as_dict(self, receiver: TransactionAttemptReceiver) -> dict:
        res = dict()  # type: Any

        res[TransactionAttemptReceiver.DICT_ADDRESS_KEY] = receiver.address
        res[TransactionAttemptReceiver.DICT_AMOUNT_KEY] = str(receiver.amount)

        return res

    def _attempt_as_dict(self, attempt: TransactionAttempt) -> dict:
        res = dict()  # type: Any

        res[TransactionAttempt.DICT_CURRENCY] = attempt.currency
        res[TransactionAttempt.DICT_FEE] = str(attempt.fee)
        res[TransactionAttempt.DICT_SENDER] = attempt.sender
        res[TransactionAttempt.DICT_RECEIVERS] = map_array(self._receiver_as_dict, attempt.receivers)

        return res

    # noinspection PyMethodMayBeStatic
    def _trigger_as_dict(self, trigger: AttemptListTrigger):
        res = dict()

        res[AttemptListTrigger.DICT_RECEIVER] = trigger.receiver
        res[AttemptListTrigger.DICT_TX] = trigger.tx
        res[AttemptListTrigger.DICT_CURRENCY] = trigger.currency

        if trigger.senders is not None:
            res[AttemptListTrigger.DICT_SENDERS_KEY] = map_array(self._sender_as_dict, trigger.senders)

        return res

    def attempt_list_as_dict(self, attempt_list: TransactionAttemptList):
        res = dict()

        res[TransactionAttemptList.DICT_ID] = attempt_list.attempt_list_id
        res[TransactionAttemptList.DICT_TRANSACTIONS] = attempt_list.transactions
        res[TransactionAttemptList.DICT_ATTEMPTS] = map_array(self._attempt_as_dict, attempt_list.attempts)
        res[TransactionAttemptList.DICT_TRIGGER] = self._trigger_as_dict(attempt_list.trigger)
        res[TransactionAttemptList.DICT_TRIES] = attempt_list.tries

        if attempt_list.last_modified is not None:
            res[TransactionAttemptList.DICT_LAST_MODIFIED] = attempt_list.last_modified

        if attempt_list.created_at is not None:
            res[TransactionAttemptList.DICT_CREATED_AT] = attempt_list.created_at

        return res

    # noinspection PyMethodMayBeStatic
    def _receiver_from_dict(self, data: dict) -> TransactionAttemptReceiver:
        return TransactionAttemptReceiver(
            amount=int(data[TransactionAttemptReceiver.DICT_AMOUNT_KEY]),
            address=data[TransactionAttemptReceiver.DICT_ADDRESS_KEY])

    # noinspection PyMethodMayBeStatic
    def _sender_from_dict(self, data: dict) -> TransactionSender:
        return TransactionSender(address=data[TransactionSender.DICT_ADDRESS_KEY])

    def _sender_as_dict(self, sender: TransactionSender) -> dict:
        res = dict()
        res[TransactionSender.DICT_ADDRESS_KEY] = sender.address
        return res

    def _attempt_from_dict(self, data: dict) -> TransactionAttempt:
        return TransactionAttempt(
            currency=data[TransactionAttempt.DICT_CURRENCY],
            fee=int(data[TransactionAttempt.DICT_FEE]),
            sender=data[TransactionAttempt.DICT_SENDER],
            receivers=map_array(self._receiver_from_dict, data[TransactionAttempt.DICT_RECEIVERS]))

    # noinspection PyMethodMayBeStatic
    def _trigger_from_dict(self, data: dict) -> AttemptListTrigger:
        if AttemptListTrigger.DICT_SENDERS_KEY in data:
            senders = map_array(self._sender_from_dict, data[AttemptListTrigger.DICT_SENDERS_KEY])
        else:
            senders = None

        return AttemptListTrigger(
            tx=data[AttemptListTrigger.DICT_TX],
            receiver=data[AttemptListTrigger.DICT_RECEIVER],
            currency=data[AttemptListTrigger.DICT_CURRENCY],
            senders=senders)

    def attempt_list_from_dict(self, data: dict) -> TransactionAttemptList:
        created_at = None
        last_modified = None
        tries = TransactionAttemptList.DEFAULT_TRIES

        if TransactionAttemptList.DICT_CREATED_AT in data:
            created_at = data[TransactionAttemptList.DICT_CREATED_AT]

        if TransactionAttemptList.DICT_LAST_MODIFIED in data:
            last_modified = data[TransactionAttemptList.DICT_LAST_MODIFIED]

        if TransactionAttemptList.DICT_TRIES in data:
            tries = data[TransactionAttemptList.DICT_TRIES]

        return TransactionAttemptList(
            trigger=self._trigger_from_dict(data[TransactionAttemptList.DICT_TRIGGER]),
            attempts=map_array(self._attempt_from_dict, data[TransactionAttemptList.DICT_ATTEMPTS]),
            transactions=data[TransactionAttemptList.DICT_TRANSACTIONS],
            last_modified=last_modified,
            created_at=created_at,
            tries=tries,
            attempt_list_id=data[TransactionAttemptList.DICT_ID])
