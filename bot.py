import json
import asyncio
from telegram.ext import Application
from web3 import Web3
import aiohttp
from config import ( 
    ETH_RPC_URL, 
    BASE_RPC_URL,
    ARB_RPC_URL,
    BSC_RPC_URL,
    POLYGON_RPC_URL,
    AVAX_RPC_URL,
    SOL_RPC_URL
)
import time
import os
import dotenv
from telegrammanage import load_blacklist

from web3.middleware import geth_poa_middleware

last_block = {}
lock = asyncio.Lock()


dotenv.load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

BLACKLIST_FILE = "blacklist.json"

processed_tx = set()  # Set to track processed tokens

# Initialize Web3 connections for each chain

#UNCOMMENT FOR OTHER CHAINS (Solana is always enabled)

web3_connections = {
    'eth': Web3(Web3.HTTPProvider(ETH_RPC_URL)),
    #'base': Web3(Web3.HTTPProvider(BASE_RPC_URL)),
    #'arbitrum': Web3(Web3.HTTPProvider(ARB_RPC_URL)),
    #'bsc': Web3(Web3.HTTPProvider(BSC_RPC_URL)),
    #'polygon': Web3(Web3.HTTPProvider(POLYGON_RPC_URL)),
    #'avalanche': Web3(Web3.HTTPProvider(AVAX_RPC_URL))
}

# Chain Explorer URLs
EXPLORERS = {
    'eth': 'https://etherscan.io',
    'base': 'https://basescan.org',
    'arbitrum': 'https://arbiscan.io',
    'bsc': 'https://bscscan.com',
    'polygon': 'https://polygonscan.com',
    'avalanche': 'https://snowtrace.io'
}

# DEXScreener URLs
DEXSCREENER_URLS = {
    'eth': 'https://dexscreener.com/ethereum',
    'base': 'https://dexscreener.com/base',
    'arbitrum': 'https://dexscreener.com/arbitrum',
    'bsc': 'https://dexscreener.com/bsc',
    'polygon': 'https://dexscreener.com/polygon',
    'avalanche': 'https://dexscreener.com/avalanche'
}

# ERC20 Transfer Event ABI
TRANSFER_ABI = {
    "anonymous": False,
    "inputs": [
        {"indexed": True, "name": "from", "type": "address"},
        {"indexed": True, "name": "to", "type": "address"},
        {"indexed": False, "name": "value", "type": "uint256"}
    ],
    "name": "Transfer",
    "type": "event"
}

# Token ABI for getting symbol and decimals
TOKEN_ABI = [
    {
        "constant": True,
        "inputs": [],
        "name": "symbol",
        "outputs": [{"name": "", "type": "string"}],
        "type": "function"
    },
    {
        "constant": True,
        "inputs": [],
        "name": "decimals",
        "outputs": [{"name": "", "type": "uint8"}],
        "type": "function"
    }
]

def is_solana_address(address):
    """Check if address is a Solana address"""
    return len(address) == 44 and not address.startswith('0x')

async def load_wallet_addresses():
    """Load wallet addresses from JSON"""
    try:
        with open('wallets.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


bot = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

async def send_telegram_message(message):
    """Send message to Telegram channel"""
    print("SENDING TELEGRAM MESSAGE")
    #await test_notification.send_test_message()
    async with bot:
        await bot.bot.send_message(
            chat_id=TELEGRAM_CHAT_ID,
            text=message,
            parse_mode='HTML',
            disable_web_page_preview=True)

def get_token_info(w3, token_address):
    """Get token information from contract"""
    try:
        token_contract = w3.eth.contract(address=w3.to_checksum_address(token_address), abi=TOKEN_ABI)
        symbol = token_contract.functions.symbol().call()
        decimals = token_contract.functions.decimals().call()
        return symbol, decimals
    except Exception as e:
        print(f"Error getting token info: {str(e)}")
        return "UNKNOWN", 18


async def send_request(url, jsonxd):
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=jsonxd) as response:
            # Wait for the response and ensure it's returned as JSON
            return await response.json()
        
async def send_get_request(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            # Wait for the response and ensure it's returned as JSON
            return await response.json()


def is_token_processed(tx, wallet_address):
    transaction = (tx, wallet_address)
    if transaction in processed_tx:
        return True
    else:
        processed_tx.add(transaction)
        return False


async def monitor_solana_wallet(wallet_address, label):
    """Monitor a Solana wallet for token purchases"""
    last_signature = None
   
    try:
        # Get recent token purchases
        url = f"{SOL_RPC_URL}"
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "getSignaturesForAddress",
            "params": [
                wallet_address,
                {"limit": 5}
            ]
        }
        #era time
        await asyncio.sleep(5)
        response = await send_request(url, jsonxd=payload)
        data = response                
        print("Checking address: ", wallet_address)
        print("Checking response: ", json.dumps(response))
        
        if 'result' in data and data['result']:
            latest_signature = data['result'][0]['signature']
            
            if latest_signature != last_signature:
                # Get transaction details
                tx_payload = {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "getTransaction",
                    "params": [
                        latest_signature,
                        {"encoding": "jsonParsed", "maxSupportedTransactionVersion": 0}
                    ]
                }
                # era time
                await asyncio.sleep(4)
                tx_response = await send_request(url, jsonxd=tx_payload)
                tx_data = tx_response
                print("Checking tx: ", json.dumps(tx_response))
                
                if 'result' in tx_data and tx_data['result']:
                    # Check if it's a token purchase
                    if 'meta' in tx_data['result'] and 'postTokenBalances' in tx_data['result']['meta']:
                        post_balances = tx_data['result']['meta']['postTokenBalances']
                        pre_balances = tx_data['result']['meta']['preTokenBalances']
                        # Check for new tokens
                        for post_balance in post_balances:
                            if any(pre['mint'] == post_balance['mint'] and pre['owner'] != post_balance['owner'] for pre in pre_balances):
                                token_mint = post_balance['mint']

                                blackList = load_blacklist()

                                if is_token_processed(latest_signature, wallet_address) == False and token_mint not in blackList['blacklistMint']:
                                    print("WTF A NEW TRANSACTIONNNNN")
                                    
                                    # Get token info from Jupiter API
                                    jupiter_url = f"https://api.jup.ag/price/v2?ids={token_mint}"
                                    token_info = await send_get_request(jupiter_url)
                                    print("CHECKING PRICE ON JUP ", json.dumps(token_info))
                                    
                                    if 'data' in token_info and token_mint in token_info['data']:
                                        token_data = token_info['data'][token_mint]
                                        message = (
                                            f" New Token Purchase on Solana by {label}!\n\n"
                                            f"Holding Address: {wallet_address}\n"
                                            f"Token Address: [{token_mint}]\n"
                                            f"Price: ${token_data['price']}\n"
                                            f"Chart: https://dexscreener.com/solana/{token_mint}\n"
                                            f"Transaction: https://solscan.io/tx/{latest_signature}"
                                        )
                                        await send_telegram_message(message)
            
            last_signature = latest_signature
                
    except Exception as e:
        print(f"Error monitoring Solana wallet {wallet_address}: {str(e)}")

        await asyncio.sleep(15)
async def monitor_evm_wallet(wallet_address, label):
    """Monitor an EVM wallet across multiple chains for token purchases"""
    
    async with lock:
        # Initialize last block for each chain if it's the first time
        for chain in web3_connections:
            if chain not in last_block:
                last_block[chain] = web3_connections[chain].eth.block_number
    
    print("wallet_address: ", wallet_address)
    for chain, w3 in web3_connections.items():
        try:
            current_block = w3.eth.block_number
            if current_block > last_block[chain]:
                # Get new blocks
                print(current_block)
                for block_number in range(last_block[chain] + 1, current_block + 1):
                    if geth_poa_middleware not in w3.middleware_onion:
                        w3.middleware_onion.inject(geth_poa_middleware, layer=0)
                        
                    block = w3.eth.get_block(block_number, full_transactions=True)
                    print("CHECKING EVM, Block Number:: ", current_block)
                    for tx in block.transactions:
                        if isinstance(tx, dict) and tx['from'].lower() == wallet_address.lower():
                            # Check if this is a token swap/purchase
                            if tx.get('to') and tx.get('input').startswith('0x'):
                                try:
                                    # Get token details
                                    token_address = tx['to']
                                    symbol, decimals = get_token_info(w3, token_address)
                                    
                                    message = (
                                        f" New Token Purchase on {chain.upper()} by {label}!\n\n"
                                        f"Holding Address: {wallet_address}\n"
                                        f"Token: {symbol}\n"
                                        f"Contract: [{token_address}]\n"
                                        f"Chart: {DEXSCREENER_URLS[chain]}/{token_address}\n"
                                        f"Transaction: {EXPLORERS[chain]}/tx/{tx['hash'].hex()}"
                                    )
                                    
                                    await send_telegram_message(message)
                                except Exception as e:
                                    print(f"Error processing transaction: {str(e)}")
                
                async with lock:
                    last_block[chain] = current_block
                    print(f"Updated last block for {chain}: {last_block[chain]}")
                
        except Exception as e:
            print(f"Error monitoring {chain} wallet {wallet_address}: {str(e)}")
    await asyncio.sleep(5)


async def main():
    while True:
        # Load wallet addresses from the JSON file
        wallets = await load_wallet_addresses()
        
        # For each wallet, run its monitoring function one at a time
        for label, address in wallets.items():
            await monitor_wallet(address, label)
        
        print("All wallets have been checked. Restarting in 20 seconds...")
        await asyncio.sleep(20)

async def monitor_wallet(address, label):
    """Monitor a single wallet every 10 seconds"""
    if is_solana_address(address):
        await monitor_solana_wallet(address, label)
    else:
        await monitor_evm_wallet(address, label)
    
    # Delay 10 seconds before checking the next transaction for this wallet
    await asyncio.sleep(10)
