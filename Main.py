import asyncio
import os
import time
from pyrogram import Client, filters, errors
from pyrogram.enums import ChatAction, ParseMode
from pyrogram.types import ChatPrivileges

API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
STRING_SESSION = os.environ.get("STRING_SESSION")
OWNER_ID = int(os.environ.get("OWNER_ID"))

app = Client(
    "userbot",
    api_id=API_ID,
    api_hash=API_HASH,
    session_string=STRING_SESSION,
    parse_mode=ParseMode.HTML
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
                mention = f'<a href="tg://user?id={user.id}">{user.first_name}</a>'
                welcome_text = f"<blockquote><b>Welcome 🤗🤗 {mention}</b>\n<i>Have a great time here!</i></blockquote>"
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
        msg = "<blockquote><b>Welcomer Bot START ho gaya hai!</b> 🟢\n<i>Purani pending requests process ho rahi hain...</i></blockquote>"
        await message.reply_text(msg)
        asyncio.create_task(process_all_pending_requests(client, chat_id))
    elif "stop" in command:
        IS_ACTIVE = False
        msg = "<blockquote><b>Welcomer Bot ko STOP kar diya gaya hai!</b> 🛑\n<i>Bot abhi koi request accept nahi karega.</i></blockquote>"
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
        mention = f'<a href="tg://user?id={user.id}">{user.first_name}</a>'
        welcome_text = f"<blockquote><b>Welcome 🤗🤗 {mention}</b>\n<i>Have a great time here!</i></blockquote>"
        await client.send_message(chat_id, welcome_text)
        await asyncio.sleep(10)
    except errors.FloodWait as e:
        await asyncio.sleep(e.value)
    except Exception as e:
        print(f"Live request error: {e}")

# ==================== 2. AFK SYSTEM ====================

@app.on_message(filters.command("afk", prefixes=[".", "/"]) & filters.group)
async def set_afk(client, message):
    try:
        user = message.from_user
        if not user:
            return
        reason = "Busy"
        if len(message.command) > 1:
            reason = message.text.split(None, 1)[1]
        AFK_USERS[user.id] = {"reason": reason, "time": time.time()}
        mention = f'<a href="tg://user?id={user.id}">{user.first_name}</a>'
        msg = f"<blockquote><b>User AFK Alert!</b> 💤\n<b>User:</b> {mention}\n<b>Reason:</b> <code>{reason}</code></blockquote>"
        await message.reply_text(msg)
    except Exception as e:
        print(f"AFK Set Error: {e}")

@app.on_message(filters.group, group=1)
async def afk_listener(client, message):
    try:
        user = message.from_user
        if not user:
            return

        # 1. User wapas bola toh AFK khatam
        if user.id in AFK_USERS and not (message.text and message.text.startswith((".", "/"))):
            afk_data = AFK_USERS.pop(user.id)
            afk_duration = get_readable_time(int(time.time() - afk_data["time"]))
            mention = f'<a href="tg://user?id={user.id}">{user.first_name}</a>'
            msg = f"<blockquote><b>Welcome back {mention}!</b> 👋\n<i>Aap</i> <b>{afk_duration}</b> <i>tak AFK the.</i></blockquote>"
            await message.reply_text(msg)

        # 2. Agar AFK user ke message par reply kiya
        if message.reply_to_message and message.reply_to_message.from_user:
            replied_user = message.reply_to_message.from_user
            if replied_user.id in AFK_USERS:
                afk_data = AFK_USERS[replied_user.id]
                afk_duration = get_readable_time(int(time.time() - afk_data["time"]))
                mention = f'<a href="tg://user?id={replied_user.id}">{replied_user.first_name}</a>'
                msg = (
                    f"<blockquote>⚠️ <b>User abhi AFK hai!</b>\n"
                    f"<b>User:</b> {mention}\n"
                    f"<b>Reason:</b> <code>{afk_data['reason']}</code>\n"
                    f"<b>Duration:</b> <code>{afk_duration}</code></blockquote>"
                )
                await message.reply_text(msg)
                return

        # 3. Agar AFK user ko tag kiya
        if message.entities:
            for ent in message.entities:
                if ent.type.name == "TEXT_MENTION" and ent.user and ent.user.id in AFK_USERS:
                    afk_data = AFK_USERS[ent.user.id]
                    afk_duration = get_readable_time(int(time.time() - afk_data["time"]))
                    mention = f'<a href="tg://user?id={ent.user.id}">{ent.user.first_name}</a>'
                    msg = (
                        f"<blockquote>⚠️ <b>User abhi AFK hai!</b>\n"
                        f"<b>User:</b> {mention}\n"
                        f"<b>Reason:</b> <code>{afk_data['reason']}</code>\n"
                        f"<b>Duration:</b> <code>{afk_duration}</code></blockquote>"
                    )
                    await message.reply_text(msg)
                    break
    except Exception as e:
        print(f"AFK Listener Error: {e}")

# ==================== 3. ADMIN TOOLS ====================

@app.on_message(filters.command("ban", prefixes=[".", "/"]) & filters.group)
async def ban_cmd(client, message):
    if not await is_authorized(client, message):
        return
    target = message.reply_to_message.from_user if message.reply_to_message else None
    if not target:
        return await message.reply_text("<blockquote>⚠️ <b>Kisi ke message par reply karke .ban likhein!</b></blockquote>")
    try:
        await client.ban_chat_member(message.chat.id, target.id)
        mention = f'<a href="tg://user?id={target.id}">{target.first_name}</a>'
        await message.reply_text(f"<blockquote>🚫 <b>Banned:</b> {mention}\n<i>Group se permanently ban kar diya gaya!</i></blockquote>")
    except Exception as e:
        await message.reply_text(f"<blockquote>❌ <b>Error:</b> <code>{e}</code></blockquote>")

@app.on_message(filters.command("kick", prefixes=[".", "/"]) & filters.group)
async def kick_cmd(client, message):
    if not await is_authorized(client, message):
        return
    target = message.reply_to_message.from_user if message.reply_to_message else None
    if not target:
        return await message.reply_text("<blockquote>⚠️ <b>Kisi ke message par reply karke .kick likhein!</b></blockquote>")
    try:
        await client.ban_chat_member(message.chat.id, target.id)
        await client.unban_chat_member(message.chat.id, target.id)
        mention = f'<a href="tg://user?id={target.id}">{target.first_name}</a>'
        await message.reply_text(f"<blockquote>👢 <b>Kicked:</b> {mention}\n<i>Group se nikal diya gaya!</i></blockquote>")
    except Exception as e:
        await message.reply_text(f"<blockquote>❌ <b>Error:</b> <code>{e}</code></blockquote>")

@app.on_message(filters.command("promote", prefixes=[".", "/"]) & filters.group)
async def promote_cmd(client, message):
    if not await is_authorized(client, message):
        return
    target = message.reply_to_message.from_user if message.reply_to_message else None
    title = message.text.split(None, 1)[1][:16] if len(message.command) > 1 else "Admin"
    if not target:
        return await message.reply_text("<blockquote>⚠️ <b>Kisi ke message par reply karke .promote [title] likhein!</b></blockquote>")
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
                can_manage_video_chats=True,
                can_promote_members=True
            )
        )
        try:
            await client.set_administrator_title(message.chat.id, target.id, title)
        except Exception:
            pass
        mention = f'<a href="tg://user?id={target.id}">{target.first_name}</a>'
        await message.reply_text(f"<blockquote>👑 <b>Promoted:</b> {mention}\n<b>Title:</b> <code>{title}</code></blockquote>")
    except Exception as e:
        await message.reply_text(f"<blockquote>❌ <b>Promote Error:</b> <code>{e}</code></blockquote>")

@app.on_message(filters.command("demote", prefixes=[".", "/"]) & filters.group)
async def demote_cmd(client, message):
    if not await is_authorized(client, message):
        return
    target = message.reply_to_message.from_user if message.reply_to_message else None
    if not target:
        return await message.reply_text("<blockquote>⚠️ <b>Kisi ke message par reply karke .demote likhein!</b></blockquote>")
    try:
        await client.promote_chat_member(
            chat_id=message.chat.id,
            user_id=target.id,
            privileges=ChatPrivileges(
                can_manage_chat=False,
                can_delete_messages=False,
                can_restrict_members=False,
                can_invite_users=False,
                can_pin_messages=False,
                can_manage_video_chats=False,
                can_promote_members=False
            )
        )
        mention = f'<a href="tg://user?id={target.id}">{target.first_name}</a>'
        await message.reply_text(f"<blockquote>📉 <b>Demoted:</b> {mention}\n<i>Admin status remove kar diya gaya!</i></blockquote>")
    except Exception as e:
        await message.reply_text(f"<blockquote>❌ <b>Error:</b> <code>{e}</code></blockquote>")

if __name__ == "__main__":
    print("Userbot Complete Suite is Online!")
    app.run()
            
