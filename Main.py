import asyncio
import os
import time
from pyrogram import Client, filters, errors
from pyrogram.enums import ChatAction
from pyrogram.types import ChatPermissions, ChatPrivileges

API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
STRING_SESSION = os.environ.get("STRING_SESSION")
OWNER_ID = int(os.environ.get("OWNER_ID"))

app = Client("userbot", api_id=API_ID, api_hash=API_HASH, session_string=STRING_SESSION)

IS_ACTIVE = True
TASK_RUNNING = False
AFK_USERS = {}

def get_readable_time(seconds: int) -> str:
    count = 0
    ping_time = ""
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
        ping_time += time_list.pop() + ", "
    time_list.reverse()
    ping_time += ":".join(time_list)
    return ping_time or "0s"

async def is_authorized(client, message):
    if message.from_user and message.from_user.id == OWNER_ID:
        return True
    try:
        member = await client.get_chat_member(message.chat.id, message.from_user.id)
        if member.status.name in ["OWNER", "ADMINISTRATOR"]:
            return True
    except Exception:
        pass
    return False

# ==================== 1. WELCOMER & JOIN REQUESTS ====================

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
                await asyncio.sleep(5)
                mention = f"[{user.first_name}](tg://user?id={user.id})"
                welcome_text = f"> **Welcome 🤗🤗 {mention}**\n> *Have a great time here!*"
                await client.send_message(chat_id, welcome_text)
                await asyncio.sleep(10)
            except errors.FloodWait as e:
                await asyncio.sleep(e.value)
            except Exception as e:
                print(f"Error processing user: {e}")
    except Exception as e:
        print(f"Error fetching requests: {e}")
    finally:
        TASK_RUNNING = False

@app.on_message(filters.command(["start", "stop"], prefixes=[".", "/"]) & filters.user(OWNER_ID))
async def control_bot(client, message):
    global IS_ACTIVE
    command = message.text.lower()
    chat_id = message.chat.id
    if "start" in command:
        IS_ACTIVE = True
        msg = "> **Welcomer Bot START ho gaya hai!** 🟢\n> *Purani pending requests process ho rahi hain...*"
        await message.reply_text(msg)
        asyncio.create_task(process_all_pending_requests(client, chat_id))
    elif "stop" in command:
        IS_ACTIVE = False
        msg = "> **Welcomer Bot ko STOP kar diya gaya hai!** 🛑\n> *Bot abhi koi request accept nahi karega.*"
        await message.reply_text(msg)

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
        await asyncio.sleep(5)
        mention = f"[{user.first_name}](tg://user?id={user.id})"
        welcome_text = f"> **Welcome 🤗🤗 {mention}**\n> *Have a great time here!*"
        await client.send_message(chat_id, welcome_text)
        await asyncio.sleep(10)
    except errors.FloodWait as e:
        await asyncio.sleep(e.value)
    except Exception as e:
        print(f"Live request error: {e}")

# ==================== 2. AFK SYSTEM (ALL GROUP MEMBERS) ====================

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
    msg = f"> **User AFK Alert!** 💤\n> **User:** {mention}\n> **Reason:** `{reason}`"
    await message.reply_text(msg)

@app.on_message(filters.group, group=1)
async def afk_listener(client, message):
    user = message.from_user
    if not user:
        return

    # User wapas bola toh AFK khatam
    if user.id in AFK_USERS and not (message.text and message.text.startswith((".", "/"))):
        afk_data = AFK_USERS.pop(user.id)
        afk_duration = get_readable_time(int(time.time() - afk_data["time"]))
        mention = f"[{user.first_name}](tg://user?id={user.id})"
        msg = f"> **Welcome back {mention}!** 👋\n> *Aap* **{afk_duration}** *tak AFK the.*"
        await message.reply_text(msg)

    # Agar kisi AFK user ko reply kiya
    if message.reply_to_message and message.reply_to_message.from_user:
        replied_user = message.reply_to_message.from_user
        if replied_user.id in AFK_USERS:
            afk_data = AFK_USERS[replied_user.id]
            afk_duration = get_readable_time(int(time.time() - afk_data["time"]))
            mention = f"[{replied_user.first_name}](tg://user?id={replied_user.id})"
            msg = (
                f"> **User abhi AFK hai!** ⚠️\n"
                f"> **User:** {mention}\n"
                f"> **Reason:** `{afk_data['reason']}`\n"
                f"> **Duration:** `{afk_duration}`"
            )
            await message.reply_text(msg)
            return

    # Agar kisi AFK user ko text tag kiya
    if message.entities:
        for ent in message.entities:
            if ent.type.name == "TEXT_MENTION" and ent.user and ent.user.id in AFK_USERS:
                afk_data = AFK_USERS[ent.user.id]
                afk_duration = get_readable_time(int(time.time() - afk_data["time"]))
                mention = f"[{ent.user.first_name}](tg://user?id={ent.user.id})"
                msg = (
                    f"> **User abhi AFK hai!** ⚠️\n"
                    f"> **User:** {mention}\n"
                    f"> **Reason:** `{afk_data['reason']}`\n"
                    f"> **Duration:** `{afk_duration}`"
                )
                await message.reply_text(msg)
                break

# ==================== 3. ADMIN TOOLS (BAN / KICK / PROMOTE) ====================

@app.on_message(filters.command("ban", prefixes=[".", "/"]) & filters.group)
async def ban_cmd(client, message):
    if not await is_authorized(client, message):
        return
    target = message.reply_to_message.from_user if message.reply_to_message else None
    if not target:
        return await message.reply_text("> ⚠️ **Kisi ke message par reply karke `.ban` likhein!**")
    try:
        await client.ban_chat_member(message.chat.id, target.id)
        mention = f"[{target.first_name}](tg://user?id={target.id})"
        await message.reply_text(f"> 🚫 **Banned:** {mention}\n> *Group se permanently ban kar diya gaya!*")
    except Exception as e:
        await message.reply_text(f"> ❌ **Error:** `{e}`")

@app.on_message(filters.command("kick", prefixes=[".", "/"]) & filters.group)
async def kick_cmd(client, message):
    if not await is_authorized(client, message):
        return
    target = message.reply_to_message.from_user if message.reply_to_message else None
    if not target:
        return await message.reply_text("> ⚠️ **Kisi ke message par reply karke `.kick` likhein!**")
    try:
        await client.ban_chat_member(message.chat.id, target.id)
        await client.unban_chat_member(message.chat.id, target.id)
        mention = f"[{target.first_name}](tg://user?id={target.id})"
        await message.reply_text(f"> 👢 **Kicked:** {mention}\n> *Group se nikal diya gaya!*")
    except Exception as e:
        await message.reply_text(f"> ❌ **Error:** `{e}`")

@app.on_message(filters.command("promote", prefixes=[".", "/"]) & filters.group)
async def promote_cmd(client, message):
    if not await is_authorized(client, message):
        return
    target = message.reply_to_message.from_user if message.reply_to_message else None
    title = message.text.split(None, 1)[1][:16] if len(message.command) > 1 else "Admin"
    if not target:
        return await message.reply_text("> ⚠️ **Kisi ke message par reply karke `.promote <title>` likhein!**")
    try:
        await client.promote_chat_member(
            message.chat.id, target.id,
            privileges=ChatPrivileges(
                can_manage_chat=True, can_delete_messages=True,
                can_restrict_members=True, can_invite_users=True,
                can_pin_messages=True, can_manage_video_chats=True
            )
        )
        try:
            await client.set_administrator_title(message.chat.id, target.id, title)
        except Exception:
            pass
        mention = f"[{target.first_name}](tg://user?id={target.id})"
        await message.reply_text(f"> 👑 **Promoted:** {mention}\n> **Title:** `{title}`")
    except Exception as e:
        await message.reply_text(f"> ❌ **Error:** `{e}`")

@app.on_message(filters.command("demote", prefixes=[".", "/"]) & filters.group)
async def demote_cmd(client, message):
    if not await is_authorized(client, message):
        return
    target = message.reply_to_message.from_user if message.reply_to_message else None
    if not target:
        return await message.reply_text("> ⚠️ **Kisi ke message par reply karke `.demote` likhein!**")
    try:
        await client.promote_chat_member(
            message.chat.id, target.id,
            privileges=ChatPrivileges(
                can_manage_chat=False, can_delete_messages=False,
                can_restrict_members=False, can_invite_users=False,
                can_pin_messages=False, can_promote_members=False
            )
        )
        mention = f"[{target.first_name}](tg://user?id={target.id})"
        await message.reply_text(f"> 📉 **Demoted:** {mention}\n> *Admin status remove kar diya gaya!*")
    except Exception as e:
        await message.reply_text(f"> ❌ **Error:** `{e}`")

if __name__ == "__main__":
    print("Userbot Complete Suite is Online with Blockquotes!")
    app.run()
    
