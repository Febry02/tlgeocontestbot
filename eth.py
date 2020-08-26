import logging
from web3 import Web3, HTTPProvider
from web3.middleware import geth_poa_middleware

import settings

log = logging.getLogger(__name__)


def make_transaction(to, value):
    try:
        w3 = Web3(HTTPProvider(settings.HTTP_NODE_URL))
        w3.middleware_onion.inject(geth_poa_middleware, layer=0)

        from_addr = w3.eth.account.from_key(settings.PRIVATE_KEY).address

        contract = w3.eth.contract(settings.CONTRACT_ADDRESS, abi=settings.CONTRACT_ABI)

        txn = contract.functions.transfer(to, value).buildTransaction(
            {
                'from': from_addr,
                'gas': 10000000,
                'gasPrice': 0,
                'nonce': w3.eth.getTransactionCount(from_addr, 'pending')
            }
        )

        log.debug('Building new transaction: {}'.format(txn))

        signed_txn = w3.eth.account.sign_transaction(txn, private_key=settings.PRIVATE_KEY)
        hash = w3.eth.sendRawTransaction(signed_txn.rawTransaction)
        return hash.hex()
    except Exception as e:
        return e


def test():
    w3 = Web3(HTTPProvider(settings.HTTP_NODE_URL))
    w3.middleware_onion.inject(geth_poa_middleware, layer=0)

    from_addr = w3.eth.account.from_key(settings.PRIVATE_KEY).address
    to_addr = '0x28e0e76b14A6f3f2d351FF6cdeA0BC46c5BD091E'

    contract = w3.eth.contract(settings.CONTRACT_ADDRESS, abi=settings.CONTRACT_ABI)

    print(contract.functions.balanceOf(from_addr).call())
    print(contract.functions.balanceOf(to_addr).call())

    txn = contract.functions.transfer(to_addr, 100).buildTransaction(
        {
            'from': from_addr,
            'gas': 1000000,
            'gasPrice': 0,
            'nonce': w3.eth.getTransactionCount(from_addr)
        }
    )
    print(txn)

    signed_txn = w3.eth.account.sign_transaction(txn, private_key=settings.PRIVATE_KEY)
    print(signed_txn)

    hash = w3.eth.sendRawTransaction(signed_txn.rawTransaction)
    print(hash.hex())

    print(contract.functions.balanceOf(from_addr).call())
    print(contract.functions.balanceOf(to_addr).call())