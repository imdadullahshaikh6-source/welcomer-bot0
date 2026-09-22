import os
import sys
from pyrogram import Client

API_ID = int(os.environ.get("API_ID", 0))
API_HASH = os.environ.get("API_HASH", "")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "").strip().strip('"').strip("'")

if not BOT_TOKEN or not API_ID or not API_HASH:
    print("CRITICAL: API_ID, API_HASH ya BOT_TOKEN missing hai!")
    sys.exit(1)

app = Client(
    name="itachi_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    in_memory=True,
    plugins=dict(root="plugins")
)

if __name__ == "__main__":
    print("Bot starting up...")
    app.run()
    
