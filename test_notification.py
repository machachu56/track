import os
from dotenv import load_dotenv
from telegram.ext import Application
import asyncio

# Load environment variables
load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

async def send_test_message():
    """Send message to Telegram channel"""
    bot = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    print("SENDING TELEGRAM MESSAGE")
    async with bot:
        await bot.bot.send_message(
            chat_id=TELEGRAM_CHAT_ID,
            text="message does it work?",
            parse_mode='HTML',
            disable_web_page_preview=True
        )
if __name__ == "__main__":
    asyncio.run(send_test_message())
