import os
import sys
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors import ChatAdminRequired, RightForbidden, RPCError

# Environment Variables
API_ID = int(os.environ.get("API_ID", 0))
API_HASH = os.environ.get("API_HASH", "")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")

if not API_ID or not API_HASH or not BOT_TOKEN:
    print("ERROR: API_ID, API_HASH, ya BOT_TOKEN missing hai! Kripya ENV variables set karein.")
    sys.exit(1)

app = Client(
    "pin_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# Bot ke pin rights check karne ka function
async def bot_can_pin(client: Client, chat_id: int) -> bool:
    try:
        bot_member = await client.get_chat_member(chat_id, "me")
        if bot_member.privileges and bot_member.privileges.can_pin_messages:
            return True
        return False
    except Exception as e:
        print(f"Error checking bot privileges: {e}")
        return False

# Command bhejane wala admin hai ya nahi check karne ka function
async def user_is_admin(client: Client, chat_id: int, user_id: int) -> bool:
    try:
        member = await client.get_chat_member(chat_id, user_id)
        if member.status.name in ["ADMINISTRATOR", "OWNER"]:
            return True
        return False
    except Exception as e:
        print(f"Error checking user privileges: {e}")
        return False

# Trigger on both .pin and /pin
@app.on_message(filters.command(["pin"], prefixes=[".", "/"]) & filters.group)
async def pin_message_handler(client: Client, message: Message):
    chat_id = message.chat.id
    user_id = message.from_user.id if message.from_user else None

    # 1. Check if replied to a message
    if not message.reply_to_message:
        await message.reply_text("❌ Kripya kisi message par **reply** karke `.pin` likhein.")
        return

    # 2. Check if user is admin
    if user_id:
        is_admin = await user_is_admin(client, chat_id, user_id)
        if not is_admin:
            await message.reply_text("⚠️ Sirf group ke **Admins** hi message pin kar sakte hain.")
            return

    # 3. Check if bot has pin permission
    can_pin = await bot_can_pin(client, chat_id)
    if not can_pin:
        await message.reply_text("❌ Mere paas message **Pin** karne ki permission nahi hai! Kripya mujhe admin banayein aur pin permission dein.")
        return

    # 4. Pin the message
    target_message_id = message.reply_to_message.id
    try:
        # Check agar silent pin chahiye (.pin silent)
        notify = True
        if len(message.command) > 1 and message.command[1].lower() in ["silent", "mute", "quiet"]:
            notify = False

        await client.pin_chat_message(
            chat_id=chat_id,
            message_id=target_message_id,
            disable_notification=not notify
        )
        await message.reply_text("✅ Message successfully **Pin** ho gaya hai!")
    except ChatAdminRequired:
        await message.reply_text("❌ Admin rights missing: Bot ko Pin Messages ki permission chahiye.")
    except RightForbidden:
        await message.reply_text("❌ Telegram ne pin karne se mana kar diya (Rights forbidden).")
    except RPCError as e:
        await message.reply_text(f"❌ Error aaya: `{e.MESSAGE}`")
    except Exception as e:
        await message.reply_text(f"❌ Kuch gadbad hui: `{str(e)}`")

# Start command
@app.on_message(filters.command(["start"], prefixes=[".", "/"]))
async def start_handler(client: Client, message: Message):
    await message.reply_text(
        "👋 Hello! Main ek simple **Pin Bot** hoon.\n\n"
        "1. Mujhe apne group me add karein aur Admin banayein (Pin permission ke sath).\n"
        "2. Kisi bhi message par reply karke `.pin` ya `/pin` likhein, main us message ko pin kar dunga!"
    )

if __name__ == "__main__":
    print("Bot start ho raha hai...")
    app.run()
    
