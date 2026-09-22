import asyncio
import os
import time
from pyrogram import Client, filters, errors
from pyrogram.enums import ChatAction

API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
STRING_SESSION = os.environ.get("STRING_SESSION")

app = Client(
    "userbot",
    api_id=API_ID,
    api_hash=API_HASH,
    session_string=STRING_SESSION
)

IS_ACTIVE = True
TASK_RUNNING = False
AFK_USERS = {}

def get_readable_time(seconds: int) -> str:
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    d, h = divmod(h, 24)
    if d > 0:
        return f"{d}d {h}h"
    if h > 0:
        return f"{h}h {m}m"
    if m > 0:
        return f"{m}m {s}s"
    return f"{s}s"

# ==================== TEST COMMAND ====================
# filters.me lagane se Noor ID ke khud ke messages bhi sunega
@app.on_message(filters.command(["ping", "test"], prefixes=[".", "/"]) & (filters.group | filters.me))
async def ping_test(client, message):
    await message.reply_text("🏓 **PONG! Noor Userbot is Active and Working!**")

# ==================== START / STOP ====================
@app.on_message(filters.command(["start", "stop"], prefixes=[".", "/"]) & (filters.group | filters.me))
async def start_stop(client, message):
    global IS_ACTIVE
    cmd = message.command[0].lower()
    if cmd == "start":
        IS_ACTIVE = True
        await message.reply_text("🟢 **Welcomer Bot START ho gaya!**")
        asyncio.create_task(process_requests(client, message.chat.id))
    elif cmd == "stop":
        IS_ACTIVE = False
        await message.reply_text("🛑 **Welcomer Bot STOP ho gaya!**")

async def process_requests(client, chat_id):
    global IS_ACTIVE, TASK_RUNNING
    if TASK_RUNNING:
        return
    TASK_RUNNING = True
    try:
        async for req in client.get_chat_join_requests(chat_id):
            if not IS_ACTIVE:
                break
            try:
                await client.approve_chat_join_request(chat_id, req.user.id)
                await client.send_chat_action(chat_id, ChatAction.TYPING)
                await asyncio.sleep(4)
                await client.send_message(chat_id, f"Welcome 🤗🤗 [{req.user.first_name}](tg://user?id={req.user.id})")
                await asyncio.sleep(8)
            except Exception as e:
                print(f"Join error: {e}")
    except Exception as e:
        print(f"Fetch error: {e}")
    finally:
        TASK_RUNNING = False

# ==================== AFK SYSTEM ====================
@app.on_message(filters.command("afk", prefixes=[".", "/"]) & (filters.group | filters.me))
async def afk_handler(client, message):
    user = message.from_user
    if not user:
        return
    reason = "Busy"
    if len(message.command) > 1:
        reason = message.text.split(None, 1)[1]
    AFK_USERS[user.id] = {"reason": reason, "time": time.time()}
    await message.reply_text(f"💤 [{user.first_name}](tg://user?id={user.id}) ab **AFK** hain!\n**Reason:** `{reason}`")

@app.on_message(filters.group | filters.me, group=1)
async def afk_detect(client, message):
    user = message.from_user
    if not user:
        return

    # User wapas aaya
    if user.id in AFK_USERS and not (message.text and message.text.startswith((".", "/"))):
        data = AFK_USERS.pop(user.id)
        dur = get_readable_time(int(time.time() - data["time"]))
        await message.reply_text(f"👋 Welcome back [{user.first_name}](tg://user?id={user.id})! Aap **{dur}** tak AFK the.")

    # Reply check
    if message.reply_to_message and message.reply_to_message.from_user:
        rep = message.reply_to_message.from_user
        if rep.id in AFK_USERS:
            data = AFK_USERS[rep.id]
            dur = get_readable_time(int(time.time() - data["time"]))
            await message.reply_text(f"⚠️ [{rep.first_name}](tg://user?id={rep.id}) abhi **AFK** hain!\n**Reason:** `{data['reason']}`\n**Duration:** `{dur}`")

if __name__ == "__main__":
    print("Userbot Live and Running!")
    app.run()
    
