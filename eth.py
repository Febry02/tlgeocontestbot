import logging
from web3 import Web3, HTTPProvider

#import settings

log = logging.getLogger(__name__)

def make_transaction(to, value, private_key):
    w3 = Web3(HTTPProvider(settings.NODE_URL))

    signed_txn = w3.eth.account.signTransaction(
        dict(
            nonce=w3.eth.getTransactionCount(w3.eth.coinbase),
            gasPrice=w3.eth.gasPrice,
            gas=100000,
            to=to,
            value=value,
            data=b''
        ),
        private_key,
    )

    try:
        result = w3.eth.sendRawTransaction(signed_txn.rawTransaction)
    except Exception as e:
        return e
    return result

w3 = Web3(HTTPProvider('http://34.90.131.163:7545'))
print(w3.eth.account.from_key('F22C1F9EDF3AE0C58667C773B8AE339669055631D466CCB4F95C404E49D9B62').address)
print(w3.eth.getBalance('0xbFa087bE3D97BA04F33B50B62F31B2bBdC4F14dB'))
print(w3.eth.getBalance('0x5b4509bBD2DE2B622fa3b5f2A331b3490C9D24d3'))