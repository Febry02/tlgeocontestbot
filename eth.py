from web3 import Web3, HTTPProvider

import settings


def make_transaction(to, value, private_key):
    w3 = Web3(HTTPProvider(settings.NODE_URL))

    signed_txn = w3.eth.account.signTransaction(
        dict(
            nonce='0',
            gasPrice=w3.eth.gasPrice,
            gas=100000,
            to=to,
            value=value,
            data=b'',
        ),
        private_key,
    )

    result = w3.eth.sendRawTransaction(signed_txn.rawTransaction)
    print(result)
