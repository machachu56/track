from aiogram import Bot, Dispatcher, types, Router
from aiogram.filters import Command, CommandObject
from aiogram.types import Message, BotCommand

from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
import json
from threading import Lock
from config import TELEGRAM_BOT_TOKEN

dp = Dispatcher()
router = Router()

json_lock = Lock()

BLACKLIST_FILE = "blacklist.json"

# Function to load the blacklist JSON file
def load_blacklist():
    with json_lock:
        try:
            with open(BLACKLIST_FILE, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            return {"blacklistMint": []}

# Function to save the blacklist JSON file
def save_blacklist(blacklist_data):
    with json_lock:
        with open(BLACKLIST_FILE, "w") as f:
            json.dump(blacklist_data, f, indent=4)

async def set_commands(bot: Bot):
    commands = [
        BotCommand(command="blacklist", description="Adds token to the blacklist"),
        BotCommand(command="rmblacklist", description="Deletes a token from the blacklist"),
        BotCommand(command="lsblacklist", description="Lists blacklisted tokens"),
        BotCommand(command="start", description="start command"),
    ]
    await bot.set_my_commands(commands)


@router.message(Command(commands=["start"]))
async def start_command(message: Message):
    print("Received /start command")
    await message.answer("Welcome! This is the start command.")

# Telegram command: /blacklist
@router.message(Command(commands=["blacklist"]))
async def blacklist_token(message: types.Message, command: CommandObject):
    args = command.args  # Get arguments from the message (token to blacklist)
    
    if not args:
        await message.reply("Usage: /blacklist <mint-token>")
        return

    token = args.strip()

    # Load the current blacklist
    blacklist_data = load_blacklist()

    if token in blacklist_data["blacklistMint"]:
        await message.reply(f"The token is already blacklisted: {token}")
        return

    # Add the token to the blacklist
    blacklist_data["blacklistMint"].append(token)
    save_blacklist(blacklist_data)

    await message.reply(f"Token added to blacklist: {token}")

# Telegram command: /rmblacklist
@router.message(Command(commands=["rmblacklist"]))
async def remove_blacklist_token(message: types.Message, command: CommandObject):
    args = command.args  # Get arguments from the message (token to remove)
    
    if not args:
        await message.reply("Usage: /rmblacklist <token>")
        return

    token = args.strip()

    # Load the current blacklist
    blacklist_data = load_blacklist()

    if token not in blacklist_data["blacklistMint"]:
        await message.reply(f"The token is not in the blacklist: {token}")
        return

    # Remove the token from the blacklist
    blacklist_data["blacklistMint"].remove(token)
    save_blacklist(blacklist_data)

    await message.reply(f"Token removed from blacklist: {token}")


# Telegram command: /lsblacklist
@router.message(Command(commands=["lsblacklist"]))
async def list_blacklisted_tokens(message: types.Message):
    # Load the current blacklist
    blacklist_data = load_blacklist()

    if not blacklist_data["blacklistMint"]:
        await message.reply("The blacklist is currently empty.")
        return

    # Format and send the list of blacklisted tokens
    tokens = "\n".join(blacklist_data["blacklistMint"])
    await message.reply(f"Current blacklisted tokens:\n\n{tokens}")

# Startup logic
async def on_startup():
    print("Bot is starting...")
    await set_commands()
    print("Commands have been set.")


async def main():
    botOther = Bot(token=TELEGRAM_BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp.include_router(router)
    await dp.start_polling(botOther, on_startup=on_startup)

