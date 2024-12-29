import json
import asyncio
from telegram.ext import Application
from web3 import Web3
import requests
from config import (
    TELEGRAM_BOT_TOKEN, 
    TELEGRAM_CHAT_ID, 
    ETH_RPC_URL, 
    BASE_RPC_URL,
    ARB_RPC_URL,
    BSC_RPC_URL,
    POLYGON_RPC_URL,
    AVAX_RPC_URL,
    SOL_RPC_URL
)
import time

from web3.middleware import geth_poa_middleware


# Initialize Web3 connections for each chain
web3_connections = {
    'eth': Web3(Web3.HTTPProvider(ETH_RPC_URL)),
    'base': Web3(Web3.HTTPProvider(BASE_RPC_URL)),
    'arbitrum': Web3(Web3.HTTPProvider(ARB_RPC_URL)),
    'bsc': Web3(Web3.HTTPProvider(BSC_RPC_URL)),
    'polygon': Web3(Web3.HTTPProvider(POLYGON_RPC_URL)),
    'avalanche': Web3(Web3.HTTPProvider(AVAX_RPC_URL))
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

async def send_telegram_message(message):
    """Send message to Telegram channel"""
    bot = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    async with bot:
        await bot.bot.send_message(
            chat_id=TELEGRAM_CHAT_ID,
            text=message,
            parse_mode='HTML',
            disable_web_page_preview=True
        )

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

async def monitor_solana_wallet(wallet_address, label):
    """Monitor a Solana wallet for token purchases"""
    last_signature = None
    
    while True:
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
            time.sleep(5)
            response = requests.post(url, json=payload)
            data = response.json()                
            print("Checking address: ", wallet_address)
            print("Checking response: ", response.text)
            
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
                    time.sleep(4)
                    tx_response = requests.post(url, json=tx_payload)
                    tx_data = tx_response.json()
                    print("Checking tx: ", tx_response.text)
                    
                    if 'result' in tx_data and tx_data['result']:
                        # Check if it's a token purchase
                        if 'meta' in tx_data['result'] and 'postTokenBalances' in tx_data['result']['meta']:
                            post_balances = tx_data['result']['meta']['postTokenBalances']
                            pre_balances = tx_data['result']['meta']['preTokenBalances']
                            print("Token purchase detected")
                            # Check for new tokens
                            for post_balance in post_balances:
                                if not any(pre['mint'] == post_balance['mint'] for pre in pre_balances):
                                    token_mint = post_balance['mint']
                                    
                                    # Get token info from Jupiter API
                                    jupiter_url = f"https://api.jup.ag/price/v2?ids={token_mint}"
                                    token_info = requests.get(jupiter_url)
                                    print("CHECKING PRICE ON JUP ", token_info.text)
                                    token_info = token_info.json()
                                    
                                    if 'data' in token_info and token_mint in token_info['data']:
                                        token_data = token_info['data'][token_mint]
                                        message = (
                                            f" New Token Purchase on Solana by {label}!\n\n"
                                            f"Token: {token_data.get('symbol', 'Unknown')}\n"
                                            f"Token Address: {token_mint}\n"
                                            f"Price: ${token_data.get('price', 'Unknown')}\n"
                                            f"Chart: https://dexscreener.com/solana/{token_mint}\n"
                                            f"Transaction: https://solscan.io/tx/{latest_signature}"
                                        )
                                        await send_telegram_message(message)
                
                last_signature = latest_signature
                
        except Exception as e:
            print(f"Error monitoring Solana wallet {wallet_address}: {str(e)}")

        await asyncio.sleep(5)
async def monitor_evm_wallet(wallet_address, label):
    """Monitor an EVM wallet across multiple chains for token purchases"""
    last_block = {}
    
    # Initialize last block for each chain
    for chain in web3_connections:
        try:
            last_block[chain] = web3_connections[chain].eth.block_number
        except:
            last_block[chain] = 0
    
    while True:
        for chain, w3 in web3_connections.items():
            try:
                current_block = w3.eth.block_number
                
                if current_block > last_block[chain]:
                    # Get new blocks
                    for block_number in range(last_block[chain] + 1, current_block + 1):
                        if geth_poa_middleware not in w3.middleware_onion:
                            w3.middleware_onion.inject(geth_poa_middleware, layer=0)
                            
                        block = w3.eth.get_block(block_number, full_transactions=True)
                        
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
                                            f"Token: {symbol}\n"
                                            f"Contract: {token_address}\n"
                                            f"Chart: {DEXSCREENER_URLS[chain]}/{token_address}\n"
                                            f"Transaction: {EXPLORERS[chain]}/tx/{tx['hash'].hex()}"
                                        )
                                        
                                        await send_telegram_message(message)
                                    except Exception as e:
                                        print(f"Error processing transaction: {str(e)}")
                    
                    last_block[chain] = current_block
                    
            except Exception as e:
                print(f"Error monitoring {chain} wallet {wallet_address}: {str(e)}")
        await asyncio.sleep(5)
async def main():
    """Main function to start monitoring all wallets"""
    wallets = await load_wallet_addresses()
    tasks = []
    
    for label, address in wallets.items():
        if is_solana_address(address):
            task = asyncio.create_task(monitor_solana_wallet(address, label))
        else:
            task = asyncio.create_task(monitor_evm_wallet(address, label))
        tasks.append(task)
    
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())
