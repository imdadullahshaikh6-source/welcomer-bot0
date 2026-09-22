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

# Aapki Itachi wali numeric Telegram ID
ITACHI_ID = 8373739674

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

def is_admin_or_owner(message):
    # Noor khud bhej rahi ho (outgoing)
    if message.outgoing:
        return True
    # Itachi ID se message aaya ho (incoming)
    if message.from_user and message.from_user.id == ITACHI_ID:
        return True
    return False

# ==================== JOIN WELCOMER ====================

async def process_requests(client, chat_id):
    global IS_ACTIVE, TASK_RUNNING
    if TASK_RUNNING:
        return
    TASK_RUNNING = True
    try:
        chat = await client.get_chat(chat_id)
        async for req in client.get_chat_join_requests(chat.id):
            if not IS_ACTIVE:
                break
            try:
                await client.approve_chat_join_request(chat.id, req.user.id)
                await client.send_chat_action(chat.id, ChatAction.TYPING)
                await asyncio.sleep(4)
                name = re.sub(r'[*_`\[\]()]', '', req.user.first_name or "User")
                await client.send_message(chat.id, f"Welcome 🤗🤗 [{name}](tg://user?id={req.user.id})")
                await asyncio.sleep(8)
            except errors.FloodWait as e:
                await asyncio.sleep(e.value)
            except Exception as e:
                print(f"Approval error: {e}")
    except Exception as e:
        print(f"Fetch error: {e}")
    finally:
        TASK_RUNNING = False

@app.on_message(filters.regex(r"^[./](?i)(start|stop)") & filters.group)
async def start_stop_handler(client, message):
    if not is_admin_or_owner(message):
        return
    global IS_ACTIVE
    text = message.text.lower()
    if "start" in text:
        IS_ACTIVE = True
        await message.reply_text("🟢 **Welcomer Bot START ho gaya!**")
        asyncio.create_task(process_requests(client, message.chat.id))
    elif "stop" in text:
        IS_ACTIVE = False
        await message.reply_text("🛑 **Welcomer Bot STOP ho gaya!**")

@app.on_chat_join_request()
async def live_join_handler(client, request):
    global IS_ACTIVE
    if not IS_ACTIVE:
        return
    try:
        await client.approve_chat_join_request(request.chat.id, request.from_user.id)
        await client.send_chat_action(request.chat.id, ChatAction.TYPING)
        await asyncio.sleep(4)
        name = re.sub(r'[*_`\[\]()]', '', request.from_user.first_name or "User")
        await client.send_message(request.chat.id, f"Welcome 🤗🤗 [{name}](tg://user?id={request.from_user.id})")
    except Exception as e:
        print(f"Live join error: {e}")

# ==================== AFK SYSTEM (FOR ALL MEMBERS) ====================

@app.on_message(filters.regex(r"^[./](?i)afk(\s+[\s\S]+)?$") & filters.group)
async def afk_set_handler(client, message):
    user = message.from_user
    if not user:
        return
    parts = message.text.split(maxsplit=1)
    reason = parts[1] if len(parts) > 1 else "Busy"
    AFK_USERS[user.id] = {"reason": reason, "time": time.time()}
    name = re.sub(r'[*_`\[\]()]', '', user.first_name or "User")
    await message.reply_text(f"💤 [{name}](tg://user?id={user.id}) ab **AFK** hain!\n**Reason:** `{reason}`")

@app.on_message(filters.group, group=1)
async def afk_listener_handler(client, message):
    user = message.from_user
    if not user:
        return

    # User wapas aaya
    if user.id in AFK_USERS and not (message.text and message.text.startswith((".", "/"))):
        data = AFK_USERS.pop(user.id)
        dur = get_readable_time(int(time.time() - data["time"]))
        name = re.sub(r'[*_`\[\]()]', '', user.first_name or "User")
        await message.reply_text(f"👋 Welcome back [{name}](tg://user?id={user.id})! Aap **{dur}** tak AFK the.")

    # Reply check
    if message.reply_to_message and message.reply_to_message.from_user:
        rep = message.reply_to_message.from_user
        if rep.id in AFK_USERS:
            data = AFK_USERS[rep.id]
            dur = get_readable_time(int(time.time() - data["time"]))
            name = re.sub(r'[*_`\[\]()]', '', rep.first_name or "User")
            await message.reply_text(f"⚠️ [{name}](tg://user?id={rep.id}) abhi **AFK** hain!\n**Reason:** `{data['reason']}`\n**Duration:** `{dur}`")
            return

    # Mention check
    if message.entities:
        for ent in message.entities:
            if ent.type.name == "TEXT_MENTION" and ent.user and ent.user.id in AFK_USERS:
                data = AFK_USERS[ent.user.id]
                dur = get_readable_time(int(time.time() - data["time"]))
                name = re.sub(r'[*_`\[\]()]', '', ent.user.first_name or "User")
                await message.reply_text(f"⚠️ [{name}](tg://user?id={ent.user.id}) abhi **AFK** hain!\n**Reason:** `{data['reason']}`\n**Duration:** `{dur}`")
                break

# ==================== ADMIN TOOLS (ITACHI & NOOR EXCLUSIVE) ====================

@app.on_message(filters.regex(r"^[./](?i)promote(\s+[\s\S]+)?$") & filters.group)
async def promote_handler(client, message):
    if not is_admin_or_owner(message):
        return
    target = message.reply_to_message.from_user if message.reply_to_message else None
    if not target:
        return await message.reply_text("⚠️ Kisi ke message par reply karke `.promote <title>` likhein.")

    parts = message.text.split(maxsplit=1)
    title = parts[1][:16] if len(parts) > 1 else "Admin"

    try:
        await client.promote_chat_member(
            chat_id=message.chat.id,
            user_id=target.id,
            privileges=ChatPrivileges(
                can_manage_chat=True,
                can_delete_messages=True,
                can_restrict_members=True,
                can_invite_users=True,
                can_pin_messages=True,
                can_manage_video_chats=True
            )
        )
        try:
            await client.set_administrator_title(message.chat.id, target.id, title)
        except Exception:
            pass
        name = re.sub(r'[*_`\[\]()]', '', target.first_name or "User")
        await message.reply_text(f"👑 [{name}](tg://user?id={target.id}) ko Promote kar diya gaya!\n**Title:** `{title}`")
    except Exception as e:
        await message.reply_text(f"❌ Promote error: `{e}`")

@app.on_message(filters.regex(r"^[./](?i)demote") & filters.group)
async def demote_handler(client, message):
    if not is_admin_or_owner(message):
        return
    target = message.reply_to_message.from_user if message.reply_to_message else None
    if not target:
        return await message.reply_text("⚠️ Kisi admin ke message par reply karke `.demote` likhein.")

    try:
        await client.promote_chat_member(
            chat_id=message.chat.id,
            user_id=target.id,
            privileges=ChatPrivileges()
        )
        name = re.sub(r'[*_`\[\]()]', '', target.first_name or "User")
        await message.reply_text(f"📉 [{name}](tg://user?id={target.id}) ko Demote kar diya gaya!")
    except Exception as e:
        await message.reply_text(f"❌ Demote error: `{e}`")

@app.on_message(filters.regex(r"^[./](?i)kick") & filters.group)
async def kick_handler(client, message):
    if not is_admin_or_owner(message):
        return
    target = message.reply_to_message.from_user if message.reply_to_message else None
    if not target:
        return await message.reply_text("⚠️ Kisi ke message par reply karke `.kick` likhein.")

    try:
        await client.ban_chat_member(message.chat.id, target.id)
        await client.unban_chat_member(message.chat.id, target.id)
        name = re.sub(r'[*_`\[\]()]', '', target.first_name or "User")
        await message.reply_text(f"👢 [{name}](tg://user?id={target.id}) ko Kick kar diya gaya!")
    except Exception as e:
        await message.reply_text(f"❌ Kick error: `{e}`")

@app.on_message(filters.regex(r"^[./](?i)ban") & filters.group)
async def ban_handler(client, message):
    if not is_admin_or_owner(message):
        return
    target = message.reply_to_message.from_user if message.reply_to_message else None
    if not target:
        return await message.reply_text("⚠️ Kisi ke message par reply karke `.ban` likhein.")

    try:
        await client.ban_chat_member(message.chat.id, target.id)
        name = re.sub(r'[*_`\[\]()]', '', target.first_name or "User")
        await message.reply_text(f"🚫 [{name}](tg://user?id={target.id}) ko Ban kar diya gaya!")
    except Exception as e:
        await message.reply_text(f"❌ Ban error: `{e}`")

if __name__ == "__main__":
    print("Userbot Active - Fully Listening to Itachi & Noor!")
    app.run()
    
