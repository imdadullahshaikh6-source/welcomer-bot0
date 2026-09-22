import asyncio
import os
import time
from pyrogram import Client, filters, errors
from pyrogram.enums import ChatAction

API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
STRING_SESSION = os.environ.get("STRING_SESSION")
OWNER_ID = int(os.environ.get("OWNER_ID"))

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
    count = 0
    time_list = []
    time_suffix_list = ["s", "m", "h", "days"]
    while count < 4:
        count += 1
        remainder, result = divmod(seconds, 60) if count < 3 else divmod(seconds, 24)
        if seconds == 0 and remainder == 0:
            break
        time_list.append(int(result))
        seconds = int(remainder)
    for x in range(len(time_list)):
        time_list[x] = str(time_list[x]) + time_suffix_list[x]
    if len(time_list) == 4:
        time_list.pop()
    time_list.reverse()
    return ":".join(time_list) or "0s"

async def is_authorized(client, message):
    if not message.from_user:
        return False
    if message.from_user.id == OWNER_ID or message.outgoing:
        return True
    try:
        member = await client.get_chat_member(message.chat.id, message.from_user.id)
        if member.status.name in ["OWNER", "ADMINISTRATOR"]:
            return True
    except Exception:
        pass
    return False

# ==================== PING & CONTROL ====================

@app.on_message(filters.command("ping", prefixes=[".", "/"]) & filters.group)
async def ping_cmd(client, message):
    if await is_authorized(client, message):
        await message.reply_text("🏓 **Pong! Bot active hai!**")

@app.on_message(filters.command("start", prefixes=[".", "/"]) & filters.user(OWNER_ID))
async def start_bot(client, message):
    global IS_ACTIVE
    IS_ACTIVE = True
    await message.reply_text("🟢 **Welcomer Bot START ho gaya hai!**")

@app.on_message(filters.command("stop", prefixes=[".", "/"]) & filters.user(OWNER_ID))
async def stop_bot(client, message):
    global IS_ACTIVE
    IS_ACTIVE = False
    await message.reply_text("🛑 **Welcomer Bot STOP kar diya gaya hai!**")

# ==================== AFK SYSTEM ====================

@app.on_message(filters.command("afk", prefixes=[".", "/"]) & filters.group)
async def set_afk(client, message):
    user = message.from_user
    if not user:
        return
    reason = "Busy"
    if len(message.command) > 1:
        reason = message.text.split(None, 1)[1]
    
    AFK_USERS[user.id] = {"reason": reason, "time": time.time()}
    mention = f"[{user.first_name}](tg://user?id={user.id})"
    await message.reply_text(f"💤 {mention} ab **AFK** ho gaye hain!\n**Reason:** `{reason}`")

@app.on_message(filters.group, group=1)
async def afk_listener(client, message):
    user = message.from_user
    if not user:
        return

    # Wapas aane par AFK remove
    if user.id in AFK_USERS and not (message.text and message.text.startswith((".", "/"))):
        afk_data = AFK_USERS.pop(user.id)
        duration = get_readable_time(int(time.time() - afk_data["time"]))
        mention = f"[{user.first_name}](tg://user?id={user.id})"
        await message.reply_text(f"👋 Welcome back {mention}! Aap **{duration}** tak AFK the.")

    # Reply check
    if message.reply_to_message and message.reply_to_message.from_user:
        replied_user = message.reply_to_message.from_user
        if replied_user.id in AFK_USERS:
            data = AFK_USERS[replied_user.id]
            duration = get_readable_time(int(time.time() - data["time"]))
            mention = f"[{replied_user.first_name}](tg://user?id={replied_user.id})"
            await message.reply_text(f"⚠️ {mention} abhi **AFK** hain!\n**Reason:** `{data['reason']}`\n**Duration:** `{duration}`")

    # Mention check
    if message.entities:
        for ent in message.entities:
            if ent.type.name == "TEXT_MENTION" and ent.user and ent.user.id in AFK_USERS:
                data = AFK_USERS[ent.user.id]
                duration = get_readable_time(int(time.time() - data["time"]))
                mention = f"[{ent.user.first_name}](tg://user?id={ent.user.id})"
                await message.reply_text(f"⚠️ {mention} abhi **AFK** hain!\n**Reason:** `{data['reason']}`\n**Duration:** `{duration}`")
                break

if __name__ == "__main__":
    print("Userbot Stable Mode Online!")
    app.run()
    
