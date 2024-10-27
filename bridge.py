import os
import time
import random
from web3 import Web3
import json
from dotenv import load_dotenv
from colorama import Fore, Style, init
import emoji

init(autoreset=True)

load_dotenv()

sepolia_rpc_url = "https://rpc.sepolia.org"
abstract_rpc_url = "https://api.testnet.abs.xyz/"

sepolia_web3 = Web3(Web3.HTTPProvider(sepolia_rpc_url))
abstract_web3 = Web3(Web3.HTTPProvider(abstract_rpc_url))

if not sepolia_web3.is_connected():
    print(Fore.RED + "❌ Tidak terhubung ke jaringan Sepolia.")
    exit()

if not abstract_web3.is_connected():
    print(Fore.RED + "❌ Tidak terhubung ke jaringan Abstract.")
    exit()

from_address = os.getenv("FROM_ADDRESS")
private_key = os.getenv("PRIVATE_KEY")
bridge_contract_address = os.getenv("BRIDGE_CONTRACT_ADDRESS")

bridge_abi = json.loads("""
[
    {
        "constant": false,
        "inputs": [
            {"name": "_amount", "type": "uint256"},
            {"name": "_targetChainId", "type": "uint256"}
        ],
        "name": "bridgeToChain",
        "outputs": [],
        "type": "function"
    }
]
""")

sepolia_bridge_contract = sepolia_web3.eth.contract(address=bridge_contract_address, abi=bridge_abi)
abstract_bridge_contract = abstract_web3.eth.contract(address=bridge_contract_address, abi=bridge_abi)

def get_current_gas_price(web3_instance):
    return web3_instance.eth.gas_price

def generate_random_amount():
    return random.uniform(0.0000000012, 0.0000000015)

def get_balance_with_symbol(web3_instance, address):
    balance = web3_instance.eth.get_balance(address)
    return f"💰 {web3_instance.from_wei(balance, 'ether'):.8f} ETH"

def print_result(success, message):
    color = Fore.GREEN if success else Fore.RED
    symbol = emoji.emojize(":check_mark_button:") if success else emoji.emojize(":cross_mark:")
    print(color + f"{symbol} {message}")

def print_wallet_addresses(from_addr, to_addr):
    print(Fore.CYAN + f"🔄 Dari: {from_addr}  |  Untuk: {to_addr}")

def bridge_to_abstract():
    try:
        print(Fore.CYAN + f"Saldo Sepolia sebelum bridge: {get_balance_with_symbol(sepolia_web3, from_address)}")
        print_wallet_addresses(from_address, bridge_contract_address)
        
        nonce = sepolia_web3.eth.get_transaction_count(from_address)
        gas_price = get_current_gas_price(sepolia_web3)
        amount = sepolia_web3.to_wei(generate_random_amount(), 'ether')
        
        transaction = sepolia_bridge_contract.functions.bridgeToChain(amount, 11124).build_transaction({
            'from': from_address,
            'nonce': nonce,
            'gas': 2000000,
            'gasPrice': gas_price
        })
        
        signed_tx = sepolia_web3.eth.account.sign_transaction(transaction, private_key)
        tx_hash = sepolia_web3.eth.send_raw_transaction(signed_tx.raw_transaction)
        tx_receipt = sepolia_web3.eth.wait_for_transaction_receipt(tx_hash)

        if tx_receipt.status == 1:
            print_result(True, "Bridge dari Sepolia ke Abstract berhasil!")
        else:
            print_result(False, "Bridge dari Sepolia ke Abstract gagal.")
        
        print(Fore.CYAN + f"Saldo Sepolia setelah bridge: {get_balance_with_symbol(sepolia_web3, from_address)}")
    except Exception as e:
        print_result(False, f"Error: {str(e)}")

def bridge_to_sepolia():
    try:
        print(Fore.CYAN + f"Saldo Abstract sebelum bridge: {get_balance_with_symbol(abstract_web3, from_address)}")
        print_wallet_addresses(bridge_contract_address, from_address)
        
        nonce = abstract_web3.eth.get_transaction_count(from_address)
        gas_price = get_current_gas_price(abstract_web3)
        amount = abstract_web3.to_wei(generate_random_amount(), 'ether')
        
        transaction = abstract_bridge_contract.functions.bridgeToChain(amount, 11155111).build_transaction({
            'from': from_address,
            'nonce': nonce,
            'gas': 2000000,
            'gasPrice': gas_price
        })
        
        signed_tx = abstract_web3.eth.account.sign_transaction(transaction, private_key)
        tx_hash = abstract_web3.eth.send_raw_transaction(signed_tx.raw_transaction)
        tx_receipt = abstract_web3.eth.wait_for_transaction_receipt(tx_hash)

        if tx_receipt.status == 1:
            print_result(True, "Bridge dari Abstract ke Sepolia berhasil!")
        else:
            print_result(False, "Bridge dari Abstract ke Sepolia gagal.")
        
        print(Fore.CYAN + f"Saldo Abstract setelah bridge: {get_balance_with_symbol(abstract_web3, from_address)}")
    except Exception as e:
        print_result(False, f"Error: {str(e)}")

def clear_terminal():
    os.system('cls' if os.name == 'nt' else 'clear')

while True:
    bridge_to_abstract()
    time.sleep(10)
    bridge_to_sepolia()
    time.sleep(10)
    clear_terminal()
