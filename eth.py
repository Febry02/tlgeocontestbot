from web3 import Web3, HTTPProvider

import settings

def make_transaction(wallet):
    w3 = Web3(HTTPProvider(settings.ETHEREUM_NODE_URL))
    print("Latest Ethereum block number", w3.eth.blockNumber)


make_transaction('wallet')
