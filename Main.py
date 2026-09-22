import os
import sys
import asyncio
from pyrogram import Client, idle

API_ID = int(os.environ.get("API_ID", 0))
API_HASH = os.environ.get("API_HASH", "")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "").strip().strip('"').strip("'")

if not BOT_TOKEN or not API_ID or not API_HASH:
    print("CRITICAL: API_ID, API_HASH ya BOT_TOKEN missing hai!")
    sys.exit(1)

app = Client(
    "itachi_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    plugins=dict(root="plugins")
)

async def main():
    async with app:
        bot_info = await app.get_me()
        print(f"Bot successfully started as @{bot_info.username}!")
        await idle()

if __name__ == "__main__":
    asyncio.run(main())
    
