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
w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:7545"))
chain_id = 1337
my_address = "0x02c2d09e4e63217A321238581a2F75007F78a43A"
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
tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)

# Now, we have sent a Transaction to Local Blockchain
