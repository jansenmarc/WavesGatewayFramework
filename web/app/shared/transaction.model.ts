export interface Transaction {
  tx: string;
  receivers: { amount: number; address: string }[];
}
