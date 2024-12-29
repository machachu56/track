import os
from dotenv import load_dotenv
from telegram.ext import Application
import asyncio

# Load environment variables
load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

async def send_test_message():
    """Send a test message to Telegram channel"""
    bot = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    async with bot:
        await bot.bot.send_message(
            chat_id=TELEGRAM_CHAT_ID,
            text="[#1] Test Notification!\n\nYour wallet tracker bot is working correctly.\n\nTracking addresses:\n- Solana: 2abc\n- ETH: 0x0123...",
            parse_mode='HTML'
        )
        print("Test message sent!")

if __name__ == "__main__":
    asyncio.run(send_test_message())
