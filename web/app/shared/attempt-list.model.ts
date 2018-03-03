interface TransactionSender {
  address: string;
}

interface AttemptListTrigger {
  receiver: number;
  currency: 'coin' | 'waves';
  tx: string;
  senders?: TransactionSender[];
}

interface TransactionAttemptReceiver {
  address: string;
  amount: number;
}

interface TransactionAttempt {
  sender: string;
  fee: number;
  currency: string;
  receivers: TransactionAttemptReceiver[];
}

export interface TransactionAttemptList {
  trigger: AttemptListTrigger;
  attempts: TransactionAttempt[];
  transactions: string[];
  attempt_list_id: string;
}
