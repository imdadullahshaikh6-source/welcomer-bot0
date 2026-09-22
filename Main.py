import os
import sys
import asyncio
from pyrogram import Client, idle

API_ID = int(os.environ.get("API_ID", 0))
API_HASH = os.environ.get("API_HASH", "").strip().strip('"').strip("'")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "").strip().strip('"').strip("'")

if not BOT_TOKEN or not API_ID or not API_HASH:
    print("CRITICAL: API_ID, API_HASH ya BOT_TOKEN missing hai!")
    sys.exit(1)

app = Client(
    name="itachi_manager_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    in_memory=True,
    plugins=dict(root="plugins")
)

async def main():
    print("Starting Bot...")
    await app.start()
    bot_info = await app.get_me()
    print(f"Bot connected successfully as @{bot_info.username} (ID: {bot_info.id})")
    await idle()
    await app.stop()
    print("Bot stopped.")

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    
