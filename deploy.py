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

# Opening solidity contract file and reading the contents
with open("./SimpleStorage.sol", "r") as file:
    # Reading all the contents in SimpleStorage file
    simple_storage_file = file.read()

# Compiling the Smart Contract using py-solc-x
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
# compiled_code.json file contains OPCODEs and ABI
with open("compiled_code.json", "w") as file:
    json.dump(compiled_sol, file)

# Bytecode and ABI are two essential things we need to deploy a contract to the chain
# get the bytecode from json file
bytecode = compiled_sol["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["evm"][
    "bytecode"
]["object"]

# get abi from compiled_code.json file
abi = compiled_sol["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["abi"]

# How to deploy it in a simulated environment (Local Host)
# Answer: Ganache

# To deploy it to a Mainnet or Testnet we need to setup a node
# But practically it is complex process
# So we can use Node providers - like Alchemy, Infura
# we can create a project and select a network (Mainnet or Testnet) and use that project URL to connect

# Note:
# -> Make sure to check
# -> ChainId for selected network
# -> Address has enough ETH
# -> and private key is hidden

w3 = Web3(Web3.HTTPProvider(os.getenv("PROJECT_URL")))
chain_id = 4
my_address = "0x2208BdA9c7AE26b28b24a5c5D89136bc38FD74Ee"
# add '0x' before private key if it's not present
private_key = os.getenv("PRIVATE_KEY")


# To deploy with web3.py
SimpleStorage = w3.eth.contract(
    abi=abi, bytecode=bytecode
)  # This lines -> we have a contract and getting that contract's bytecode and ABI

# Get the latest transaction nonce (Note: Transaction Nonce)
nonce = w3.eth.getTransactionCount(my_address)

# -> Build a transaction
# -> Sign a transaction
# -> Send a transaction
transaction = SimpleStorage.constructor().buildTransaction(
    {
        "gasPrice": w3.eth.gas_price,
        "chainId": chain_id,
        "from": my_address,
        "nonce": nonce,
    }
)  # Inside build transaction 'gasPrice' is necessary else it'll raise a value error

# Signing the transaction with private key (make sure it is hidden)
signed_txn = w3.eth.account.sign_transaction(transaction, private_key=private_key)

# Send this signed transaction
print("Deploying Contract...")
tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
print("Waiting for TXN to finish...")
tx_receipt = w3.eth.wait_for_transaction_receipt(
    tx_hash
)  # This will stop code execution till our txn_hash gets complete

# Now, we have sent a Transaction to Blockchain (LOCAL or TESTNET or Mainnet)
print("Deployed !!!...")

# Interact and Working with contract
# When interactingwith a contract two things are necessary
# -> Contract address
# -> contract ABI

# Taking the contract address from deployed contract
simple_storage = w3.eth.contract(address=tx_receipt.contractAddress, abi=abi)

# Calling a function in a contract (doesn't charge any gas fee) (READING)
print(f"Initial Stored value: ${simple_storage.functions.retrieve().call()}")

# storing a value in a contract (Charge Gas) (because, we are changing the state of the contract)
store_txn = simple_storage.functions.store(33333).buildTransaction(
    {
        "gasPrice": w3.eth.gas_price,
        "chainId": chain_id,
        "from": my_address,
        "nonce": nonce + 1,
    }
)

# To change the state we need a TXN
signed_store_txn = w3.eth.account.sign_transaction(store_txn, private_key=private_key)
send_store_tx = w3.eth.send_raw_transaction(signed_store_txn.rawTransaction)
print("Updating stored Value")

txn_receipt = w3.eth.wait_for_transaction_receipt(
    send_store_tx
)  # Waiting for TXN to complete

print(
    simple_storage.functions.retrieve().call()
)  # printing the value we sent from the contract
