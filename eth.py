import logging
from web3 import Web3, HTTPProvider
import web3

import settings

log = logging.getLogger(__name__)


def make_transaction(to, value):
    w3 = Web3(HTTPProvider(settings.HTTP_NODE_URL))

    try:
        contract = w3.eth.contract(settings.CONTRACT_ADDRESS, abi=settings.CONTRACT_ABI)
        tx_hash = contract.functions.transfer(to, value).transact({'from': settings.TOKEN_HOLDER_ADDRESS})
        tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    except Exception as e:
        return e
    return tx_receipt

def test():
    w3 = Web3(HTTPProvider(settings.HTTP_NODE_URL))

    from_addr = settings.TOKEN_HOLDER_ADDRESS
    to_addr = '0x28e0e76b14A6f3f2d351FF6cdeA0BC46c5BD091E'

    contract = w3.eth.contract(settings.CONTRACT_ADDRESS, abi=settings.CONTRACT_ABI)

    print(contract.functions.balanceOf(from_addr).call())
    print(contract.functions.balanceOf(to_addr).call())

    tx_hash = contract.functions.transfer(to_addr, 1).transact({'from': from_addr})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)

    print(tx_hash)
    print(tx_receipt)

    print(contract.functions.balanceOf(from_addr).call())
    print(contract.functions.balanceOf(to_addr).call())
