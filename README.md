Versió en català del README aqui.

[CATALÀ](https://github.com/machachu56/track/blob/main/README_CAT.md)

English:

# Modifications of this fork

- Fixed endpoints (SOL price check, ETH RPC) Others are not tested
- Avoids Ratelimit to public RPC (Solana)
- Added commands:
  - Blacklist a token:
    - /blacklist TOKEN_ADDR
  - Removes a token from blacklist:
    - /rmblacklist TOKEN_ADDR
  - Lists blacklisted tokens:
    - /lsblacklist
**THESE COMMANDS CAN ONLY BE USED WHILE SENDING A DIRECT MESSAGE TO THE BOT - THEY CANNOT BE USED IN THE GROUP CHAT**

## Installation
To run:
1. Install requirements
```bash
pip install -r requirements.txt
```
2. Rename `.env.example` to `.env`, put your Telegram token and chat id there.
3. Rename wallets.json.example to wallets.json, add the wallets to track like this:
```json
{
    "Wallet Name 1": "0x123...",  # EVM address - Program will categorize addresses automatically.
    "Wallet Name 2": "ABC..."     # Solana address - Program will categorize addresses automatically.
}
```
4. (Optional) - Add custom RPC URLs for production use, they can be edited in `config.py`
5. Run the program:
```bash
python main.py
```

## Test Telegram Notifications
Test if the notifications are working by executing:
```bash
python test_notification.py
```

# OLD README:

## Wallet Tracker Bot

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
