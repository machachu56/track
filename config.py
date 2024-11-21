import os
from dotenv import load_dotenv

load_dotenv()

# Telegram Bot Token
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

# EVM Chain RPC URLs
ETH_RPC_URL = os.getenv('ETH_RPC_URL', 'https://eth-mainnet.g.alchemy.com/v2/your-api-key')
BASE_RPC_URL = os.getenv('BASE_RPC_URL', 'https://mainnet.base.org')
ARB_RPC_URL = os.getenv('ARB_RPC_URL', 'https://arb1.arbitrum.io/rpc')
BSC_RPC_URL = os.getenv('BSC_RPC_URL', 'https://bsc-dataseed.binance.org')
POLYGON_RPC_URL = os.getenv('POLYGON_RPC_URL', 'https://polygon-rpc.com')
AVAX_RPC_URL = os.getenv('AVAX_RPC_URL', 'https://api.avax.network/ext/bc/C/rpc')

# Solana RPC URL
SOL_RPC_URL = os.getenv('SOL_RPC_URL', 'https://api.mainnet-beta.solana.com')
