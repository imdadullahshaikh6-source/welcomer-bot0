import os
import sys
import asyncio
import traceback
from pyrogram import Client, idle

API_ID = int(os.environ.get("API_ID", 0))
API_HASH = os.environ.get("API_HASH", "").strip().strip('"').strip("'")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "").strip().strip('"').strip("'")

if not BOT_TOKEN or not API_ID or not API_HASH:
    print("CRITICAL: API_ID, API_HASH ya BOT_TOKEN missing hai!")
    sys.exit(1)

# ":memory:" uses RAM storage, so database never gets locked during Railway deploys
app = Client(
    name=":memory:",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    plugins=dict(root="plugins")
)

async def main():
    print("--- CONNECTING TO TELEGRAM MTPROTO ---")
    try:
        await app.start()
        bot_info = await app.get_me()
        print(f"SUCCESS: Bot active as @{bot_info.username} (ID: {bot_info.id})")
        await idle()
    except Exception as e:
        print("\n" + "="*50)
        print(f"BOT START CRASHED WITH ERROR: {e}")
        print("="*50 + "\n")
        traceback.print_exc()
        # Wait 30s to prevent rapid restart loops if Telegram applied FloodWait
        await asyncio.sleep(30)
        sys.exit(1)
    finally:
        try:
            await app.stop()
        except Exception:
            pass

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    
