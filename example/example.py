from typing import Optional, List, Union
import waves_gateway as gw


@gw.Injectable(gw.COIN_ADDRESS_VALIDATION_SERVICE)
class AddressValidationService(gw.AddressValidationService):

    def validate_address(self, address: str) -> bool:
        return True


@gw.Injectable(gw.COIN_CHAIN_QUERY_SERVICE)
class CustomChainQueryService(gw.ChainQueryService):

    def get_transaction_by_tx(self, tx: str) -> Optional[gw.Transaction]:
        raise NotImplementedError()

    def get_coin_receiver_address_from_transaction(self, transaction: str):
        raise NotImplementedError()

    def get_height_of_highest_block(self) -> int:
        raise NotImplementedError()

    def get_transactions_of_block_at_height(self, height: int) -> List[gw.Transaction]:
        raise NotImplementedError()


@gw.Injectable(gw.COIN_TRANSACTION_SERVICE)
class CustomTransactionService(gw.TransactionService):

    def send_coin(self, attempt: gw.TransactionAttempt, secret: Optional[str]) -> gw.Transaction:
        raise NotImplementedError()


@gw.Injectable(gw.CoinAddressFactory)
class CustomCoinAddressFactory(gw.CoinAddressFactory):
    def create_address(self) -> Union[gw.KeyPair, str]:
        return 'example'


gw.run()
