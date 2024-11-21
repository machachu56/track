# Wallet Tracker Bot

A Telegram bot that monitors wallet addresses across multiple blockchains (Ethereum, Base, Arbitrum, BSC, Polygon, Avalanche, and Solana) and sends notifications when tokens are purchased.

## Features

- Multi-chain support (EVM chains and Solana)
- Real-time token purchase notifications
- Detailed token information including:
  - Token symbol
  - Contract address/mint
  - Price (for Solana tokens)
  - Chart links (DEXScreener)
  - Transaction links
- Automatic service deployment
- Error handling and automatic restarts

## Prerequisites

- Python 3.8+
- Linux system with systemd
- Telegram Bot Token (from @BotFather)
- (Optional) RPC URLs for better performance

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/addy-tracker-bot.git
cd addy-tracker-bot
```

2. Install dependencies:
```bash
pip3 install -r requirements.txt
```

3. Create and configure environment variables:
```bash
cp .env.example .env
```
Edit `.env` with your:
- Telegram Bot Token
- Telegram Chat ID
- RPC URLs (optional)

4. Configure wallet addresses:
```bash
cp wallets.json.example wallets.json
```
Edit `wallets.json` with your wallet addresses:
```json
{
    "Wallet Name 1": "0x123...",  # EVM address
    "Wallet Name 2": "ABC..."     # Solana address
}
```

5. Set up the service:
```bash
sudo cp wallet-tracker.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable wallet-tracker.service
sudo systemctl start wallet-tracker.service
```

## Configuration

### Environment Variables

Create a `.env` file with:
```env
# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
TELEGRAM_CHAT_ID=your_telegram_chat_id_here

# EVM Chain RPC URLs (optional, defaults to public endpoints)
ETH_RPC_URL=your_ethereum_rpc_url
BASE_RPC_URL=your_base_rpc_url
ARB_RPC_URL=your_arbitrum_rpc_url
BSC_RPC_URL=your_bsc_rpc_url
POLYGON_RPC_URL=your_polygon_rpc_url
AVAX_RPC_URL=your_avalanche_rpc_url

# Solana RPC URL (optional)
SOL_RPC_URL=your_solana_rpc_url
```

### Wallet Configuration

Edit `wallets.json`:
```json
{
    "Wallet Label": "address",
    "My ETH Wallet": "0x123abc...",
    "My SOL Wallet": "ABC123..."
}
```

## Usage

The bot will automatically:
1. Monitor configured wallets
2. Detect token purchases
3. Send Telegram notifications with:
   - Token information
   - Chart links
   - Transaction details

### Service Management

```bash
# Check status
sudo systemctl status wallet-tracker.service

# View logs
sudo journalctl -u wallet-tracker.service -f

# Restart bot
sudo systemctl restart wallet-tracker.service

# Stop bot
sudo systemctl stop wallet-tracker.service
```

## Sample Notifications

### EVM Chain Purchase
```
🚨 New Token Purchase on ETH by Wallet Name!

Token: TOKEN
Contract: 0x123...
Chart: https://dexscreener.com/ethereum/0x123...
Transaction: https://etherscan.io/tx/0xabc...
```

### Solana Purchase
```
🚨 New Token Purchase on Solana by Wallet Name!

Token: TOKEN
Token Address: ABC123...
Price: $0.123
Chart: https://dexscreener.com/solana/ABC123...
Transaction: https://solscan.io/tx/XYZ...
```

## Contributing

Feel free to submit issues and enhancement requests!

## Security

- Never commit your `.env` file
- Keep your bot token private
- Use dedicated RPC URLs for production
- Monitor your logs for suspicious activity

## License

MIT License - feel free to use and modify for your needs!
