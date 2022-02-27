# compile_standart is going to be the main function to compile the solidity code
from solcx import compile_standard, install_solc
import json
from web3 import Web3
import os
from dotenv import load_dotenv

# To load environment variable from .env file
load_dotenv()

# Installing solidity version
install_solc("0.8.0")

with open("./SimpleStorage.sol", "r") as file:
    # Reading all the contents in SimpleStorage file
    simple_storage_file = file.read()

compiled_sol = compile_standard(
    {
        "language": "Solidity",
        "sources": {"SimpleStorage.sol": {"content": simple_storage_file}},
        "settings": {
            "outputSelection": {
                "*": {"*": ["abi", "metadata", "evm.bytecode", "evm.sourceMap"]}
            }
        },
    },
    solc_version="0.8.0",
)

# copying compiled code and saving it into compiled_code.json file
with open("compiled_code.json", "w") as file:
    json.dump(compiled_sol, file)

# Bytecode and ABI are two essential things we need to deploy a contract to the chain
# get the bytecode
bytecode = compiled_sol["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["evm"][
    "bytecode"
]["object"]

# get abi
abi = compiled_sol["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["abi"]

# How to deploy it in a simulated environment
# Answer: Ganache
# For connecting to ganache
w3 = Web3(
    Web3.HTTPProvider("https://rinkeby.infura.io/v3/6a283268fbfa476ebe334b9158a15ff4")
)
chain_id = 4
my_address = "0x2208BdA9c7AE26b28b24a5c5D89136bc38FD74Ee"
# add '0x' before private key if it's not present
private_key = os.getenv("PRIVATE_KEY")


# To create a contract that we are going to deploy with web3.py
SimpleStorage = w3.eth.contract(
    abi=abi, bytecode=bytecode
)  # this means we have a contract

# Get the latest transaction
nonce = w3.eth.getTransactionCount(my_address)

# Build a transaction
# Sign a transaction
# Send a transaction
transaction = SimpleStorage.constructor().buildTransaction(
    {
        "gasPrice": w3.eth.gas_price,
        "chainId": chain_id,
        "from": my_address,
        "nonce": nonce,
    }
)
# Signing the transaction
signed_txn = w3.eth.account.sign_transaction(transaction, private_key=private_key)

# send this signed transaction
print("Deploying Contract...")
tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
print("Waiting for TXN to finish...")
tx_receipt = w3.eth.wait_for_transaction_receipt(
    tx_hash
)  # This wait our code to transaction hash go through
# Now, we have sent a Transaction to Local Blockchain
print("Deployed !!!...")

# Interact and Working with contract
# -> Contract address
# -> contract ABI

simple_storage = w3.eth.contract(address=tx_receipt.contractAddress, abi=abi)
print(f"Initial Stored value: ${simple_storage.functions.retrieve().call()}")
store_txn = simple_storage.functions.store(33333).buildTransaction(
    {
        "gasPrice": w3.eth.gas_price,
        "chainId": chain_id,
        "from": my_address,
        "nonce": nonce + 1,
    }
)


signed_store_txn = w3.eth.account.sign_transaction(store_txn, private_key=private_key)
send_store_tx = w3.eth.send_raw_transaction(signed_store_txn.rawTransaction)
print("Updating stored Value")
txn_receipt = w3.eth.wait_for_transaction_receipt(send_store_tx)

print(simple_storage.functions.retrieve().call())
