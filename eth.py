import logging
from web3 import Web3, HTTPProvider

import settings

log = logging.getLogger(__name__)

def make_transaction(to, value, private_key, nonce):
    w3 = Web3(HTTPProvider(settings.NODE_URL))

    signed_txn = w3.eth.account.signTransaction(
        dict(
            nonce=nonce,
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
