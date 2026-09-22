import asyncio
import os
import time
import re
from pyrogram import Client, filters, errors
from pyrogram.enums import ChatAction
from pyrogram.types import ChatPrivileges

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
    time_list = []
    time_suffix_list = ["s", "m", "h", "days"]
    count = 0
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

# ==================== JOIN WELCOMER ====================

async def process_all_pending_requests(client, chat_id):
    global IS_ACTIVE, TASK_RUNNING
    if TASK_RUNNING:
        return
    TASK_RUNNING = True
    try:
        async for req in client.get_chat_join_requests(chat_id):
            if not IS_ACTIVE:
                break
            user = req.user
            try:
                await client.approve_chat_join_request(chat_id, user.id)
                await client.send_chat_action(chat_id, ChatAction.TYPING)
                await asyncio.sleep(4)
                clean_name = re.sub(r'[*_`\[\]()]', '', user.first_name or "User")
                mention = f"[{clean_name}](tg://user?id={user.id})"
                welcome_text = f"**Welcome 🤗🤗 {mention}**\n*Have a great time here!*"
                await client.send_message(chat_id, welcome_text)
                await asyncio.sleep(8)
            except errors.FloodWait as e:
                await asyncio.sleep(e.value)
            except Exception as e:
                print(f"Error processing user: {e}")
    except Exception as e:
        print(f"Error fetching requests: {e}")
    finally:
        TASK_RUNNING = False

@app.on_message(filters.command(["start", "stop"], prefixes=[".", "/"]) & (filters.user(OWNER_ID) | filters.me))
async def control_bot(client, message):
    global IS_ACTIVE
    command = message.text.lower()
    chat_id = message.chat.id
    if "start" in command:
        IS_ACTIVE = True
        await message.reply_text("**Welcomer Bot START ho gaya hai! 🟢**\n*Pending requests accept ho rahi hain...*")
        asyncio.create_task(process_all_pending_requests(client, chat_id))
    elif "stop" in command:
        IS_ACTIVE = False
        await message.reply_text("**Welcomer Bot STOP ho gaya hai! 🛑**")

@app.on_chat_join_request()
async def auto_accept_live(client, request):
    global IS_ACTIVE
    if not IS_ACTIVE:
        return
    chat_id = request.chat.id
    user = request.from_user
    try:
        await client.approve_chat_join_request(chat_id, user.id)
        await client.send_chat_action(chat_id, ChatAction.TYPING)
        await asyncio.sleep(4)
        clean_name = re.sub(r'[*_`\[\]()]', '', user.first_name or "User")
        mention = f"[{clean_name}](tg://user?id={user.id})"
        welcome_text = f"**Welcome 🤗🤗 {mention}**\n*Have a great time here!*"
        await client.send_message(chat_id, welcome_text)
        await asyncio.sleep(8)
    except errors.FloodWait as e:
        await asyncio.sleep(e.value)
    except Exception as e:
        print(f"Live request error: {e}")

# ==================== AFK SYSTEM ====================

@app.on_message(filters.regex(r"^[./](?i)afk(\s+[\s\S]+)?$") & filters.group)
async def set_afk(client, message):
    user = message.from_user
    if not user:
        return
    parts = message.text.split(maxsplit=1)
    reason = parts[1] if len(parts) > 1 else "Busy"
    AFK_USERS[user.id] = {"reason": reason, "time": time.time()}
    clean_name = re.sub(r'[*_`\[\]()]', '', user.first_name or "User")
    mention = f"[{clean_name}](tg://user?id={user.id})"
    await message.reply_text(f"**User AFK Alert! 💤**\n**User:** {mention}\n**Reason:** `{reason}`")

@app.on_message(filters.group, group=1)
async def afk_listener(client, message):
    user = message.from_user
    if not user:
        return

    # 1. Agar AFK user ne khud message kiya
    if user.id in AFK_USERS and not (message.text and message.text.startswith((".", "/"))):
        afk_data = AFK_USERS.pop(user.id)
        afk_duration = get_readable_time(int(time.time() - afk_data["time"]))
        clean_name = re.sub(r'[*_`\[\]()]', '', user.first_name or "User")
        mention = f"[{clean_name}](tg://user?id={user.id})"
        await message.reply_text(f"**Welcome back {mention}! 👋**\n*Aap* **{afk_duration}** *tak AFK the.*")

    # 2. Agar AFK user ko reply kiya
    if message.reply_to_message and message.reply_to_message.from_user:
        replied_user = message.reply_to_message.from_user
        if replied_user.id in AFK_USERS:
            afk_data = AFK_USERS[replied_user.id]
            afk_duration = get_readable_time(int(time.time() - afk_data["time"]))
            clean_name = re.sub(r'[*_`\[\]()]', '', replied_user.first_name or "User")
            mention = f"[{clean_name}](tg://user?id={replied_user.id})"
            await message.reply_text(
                f"⚠️ **User abhi AFK hai!**\n"
                f"**User:** {mention}\n"
                f"**Reason:** `{afk_data['reason']}`\n"
                f"**Duration:** `{afk_duration}`"
            )
            return

    # 3. Agar AFK user ko text mention kiya
    if message.entities:
        for ent in message.entities:
            if ent.type.name == "TEXT_MENTION" and ent.user and ent.user.id in AFK_USERS:
                afk_data = AFK_USERS[ent.user.id]
                afk_duration = get_readable_time(int(time.time() - afk_data["time"]))
                clean_name = re.sub(r'[*_`\[\]()]', '', ent.user.first_name or "User")
                mention = f"[{clean_name}](tg://user?id={ent.user.id})"
                await message.reply_text(
                    f"⚠️ **User abhi AFK hai!**\n"
                    f"**User:** {mention}\n"
                    f"**Reason:** `{afk_data['reason']}`\n"
                    f"**Duration:** `{afk_duration}`"
                )
                break

# ==================== ADMIN ACTIONS ====================

@app.on_message(filters.regex(r"^[./](?i)ban") & filters.group)
async def ban_cmd(client, message):
    if not await is_authorized(client, message):
        return
    target = message.reply_to_message.from_user if message.reply_to_message else None
    if not target:
        return await message.reply_text("⚠️ **Kisi ke message par reply karke .ban likhein!**")
    try:
        await client.ban_chat_member(message.chat.id, target.id)
        clean_name = re.sub(r'[*_`\[\]()]', '', target.first_name or "User")
        mention = f"[{clean_name}](tg://user?id={target.id})"
        await message.reply_text(f"🚫 **Banned:** {mention}\n*Group se permanently ban kar diya!*")
    except Exception as e:
        await message.reply_text(f"❌ Error: `{e}`")

@app.on_message(filters.regex(r"^[./](?i)kick") & filters.group)
async def kick_cmd(client, message):
    if not await is_authorized(client, message):
        return
    target = message.reply_to_message.from_user if message.reply_to_message else None
    if not target:
        return await message.reply_text("⚠️ **Kisi ke message par reply karke .kick likhein!**")
    try:
        await client.ban_chat_member(message.chat.id, target.id)
        await client.unban_chat_member(message.chat.id, target.id)
        clean_name = re.sub(r'[*_`\[\]()]', '', target.first_name or "User")
        mention = f"[{clean_name}](tg://user?id={target.id})"
        await message.reply_text(f"👢 **Kicked:** {mention}\n*Group se nikal diya!*")
    except Exception as e:
        await message.reply_text(f"❌ Error: `{e}`")

# ==================== PING CHECK ====================

@app.on_message(filters.regex(r"^[./](?i)ping") & filters.group)
async def ping_cmd(client, message):
    await message.reply_text("🏓 **Pong! Bot zinda aur active hai!**")

if __name__ == "__main__":
    print("Userbot Fully Online and Listening!")
    app.run()
                           
