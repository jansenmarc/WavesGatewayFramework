import unittest
from unittest.mock import patch, MagicMock
from typing import Any, cast

import json
from waves_gateway.common import WavesNodeException
from waves_gateway.model import Transaction, TransactionReceiver
from waves_gateway.service import WavesChainQueryServiceImpl


class WavesChainQueryServiceImplSpec(unittest.TestCase):
    def setUp(self):
        self._waves_node = 'http://fake_test_server:6969'
        self._asset_id = '23896457237'
        self._chain_query_service = cast(Any,
                                         WavesChainQueryServiceImpl(
                                             waves_node=self._waves_node, asset_id=self._asset_id))

    @patch('requests.get', autospec=True)
    def test_get_transactions_of_block_at_height(self, mock_requests_get: MagicMock):
        mock_get_result = MagicMock()
        mock_get_result.ok = True

        transactions = [{
            'signature':
            '5Kg1u9AUix8H3xkPGpHBCuFptCJJwMGkYcdRitsCuSd'
            'Zidcf19DoMNMJUKvRrRw2SjF5fGgedZJiJWwZ5DRENM64',
            'id':
            'HR96p2fuceFm2P1wbs8FtxyeoPmGooKjHmV1gHUhZ5U2',
            'assetId':
            self._asset_id,
            'amount':
            110000,
            'feeAsset':
            None,
            'fee':
            100000,
            'recipient':
            'address:3Mxjf6da1ixZD5UzM7H9rLXLWzfv5YXZvVn',
            'attachment':
            'B4GdmuG3Jbxg7DLNWu3YrXiFbdQzPiCYBGqqunsG3',
            'senderPublicKey':
            '3bwjGNumMn4K5Yzt154PFegJN4StPvdQ6HAhzbDnCP1m',
            'timestamp':
            1502026364974,
            'type':
            4,
            'sender':
            '3Mxjf6da1ixZD5UzM7H9rLXLWzfv5YXZvVn'
        }]

        mock_get_result.text = json.dumps({'transactions': transactions})

        mock_requests_get.return_value = mock_get_result

        # self._chain_query_service._get_response_from_node.return_value = {'transactions': transactions}
        transactions = self._chain_query_service.get_transactions_of_block_at_height(20)

        expected_transaction = Transaction(
            tx='HR96p2fuceFm2P1wbs8FtxyeoPmGooKjHmV1gHUhZ5U2',
            receivers=[TransactionReceiver(address='3Mxjf6da1ixZD5UzM7H9rLXLWzfv5YXZvVn', amount=110000)])

        self.assertEqual(len(transactions), 1)
        self.assertEqual(transactions[0], expected_transaction)

    @patch('requests.get', autospec=True)
    def test_get_transactions_of_block_at_height_invalid_asset_id(self, mock_requests_get: MagicMock):
        mock_get_result = MagicMock()
        mock_get_result.ok = True

        transactions = [{
            'signature':
            '5Kg1u9AUix8H3xkPGpHBCuFptCJJwMGkYcdRitsCuSd'
            'Zidcf19DoMNMJUKvRrRw2SjF5fGgedZJiJWwZ5DRENM64',
            'id':
            'HR96p2fuceFm2P1wbs8FtxyeoPmGooKjHmV1gHUhZ5U2',
            'assetId':
            '83279486572346',
            'amount':
            110000,
            'feeAsset':
            None,
            'fee':
            100000,
            'recipient':
            'address:3Mxjf6da1ixZD5UzM7H9rLXLWzfv5YXZvVn',
            'attachment':
            'B4GdmuG3Jbxg7DLNWu3YrXiFbdQzPiCYBGqqunsG3',
            'senderPublicKey':
            '3bwjGNumMn4K5Yzt154PFegJN4StPvdQ6HAhzbDnCP1m',
            'timestamp':
            1502026364974,
            'type':
            4,
            'sender':
            '3Mxjf6da1ixZD5UzM7H9rLXLWzfv5YXZvVn'
        }]

        mock_get_result.text = json.dumps({'transactions': transactions})

        mock_requests_get.return_value = mock_get_result

        transactions = self._chain_query_service.get_transactions_of_block_at_height(20)

        self.assertEqual(len(transactions), 0)

    @patch('requests.get', autospec=True)
    def test_get_transactions_of_block_at_height_node_exception(self, mock_requests_get: MagicMock):
        mock_return_value = MagicMock()
        mock_return_value.status_code = 500
        mock_return_value.text = 'Internal Server Error'
        mock_return_value.url = self._waves_node + '/blocks/at/20'
        mock_return_value.ok = False

        mock_requests_get.return_value = mock_return_value

        with self.assertRaises(WavesNodeException):
            self._chain_query_service.get_transactions_of_block_at_height(20)
