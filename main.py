import asyncio
from bot import main as bot_main
from telegrammanage import main as telegrammanage_main

async def main():
    await asyncio.gather(
        bot_main(),
        telegrammanage_main()
    )

if __name__ == "__main__":
    # Run the program :)
    asyncio.run(main())