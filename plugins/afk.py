import time
import html
from pyrogram import Client, filters
from pyrogram.enums import ParseMode, MessageEntityType
from pyrogram.types import Message

# Memory store: {user_id: {"reason": str, "time": float}}
afk_data = {}

def get_readable_time(seconds: int) -> str:
    count = 0
    time_list = []
    time_suffix_list = ["s", "m", "h", "d"]

    while count < 4:
        count += 1
        if count < 3:
            remainder, result = divmod(seconds, 60)
        else:
            remainder, result = divmod(seconds, 24)
        if seconds == 0 and remainder == 0:
            break
        time_list.append(int(result))
        seconds = int(remainder)

    hum_time = ""
    for x in range(len(time_list)):
        time_list[x] = str(time_list[x]) + time_suffix_list[x]
    if len(time_list) == 4:
        hum_time += time_list.pop() + " "
    time_list.reverse()
    hum_time += " ".join(time_list)
    return hum_time.strip() or "0s"

# ==================== .afk Command ====================
@Client.on_message(filters.command(["afk"], prefixes=[".", "/"]) & filters.group)
async def set_afk(client: Client, message: Message):
    if not message.from_user:
        return

    user_id = message.from_user.id
    user_name = html.escape(message.from_user.first_name or "User")
    mention = f"<a href='tg://user?id={user_id}'>{user_name}</a>"

    parts = message.text.split(maxsplit=1)
    reason = parts[1].strip() if len(parts) > 1 else "Busy"

    afk_data[user_id] = {
        "reason": reason,
        "time": time.time()
    }

    afk_text = (
        "<blockquote>💤 <b>𝘼𝙁𝙆 𝙉𝙤𝙩𝙞𝙘𝙚</b> 🌙\n"
        "✦ ━━━━━━━━━━━━━━━━━━ ✦\n"
        f"👤 <b>User:</b> {mention}\n"
        f"📝 <b>Reason:</b> <i>{html.escape(reason)}</i>\n"
        "✨ <i>I will notify others while you're away!</i></blockquote>"
    )

    await message.reply_text(afk_text, parse_mode=ParseMode.HTML)

# ==================== Monitor Incoming Group Messages ====================
@Client.on_message(filters.group & ~filters.bot & ~filters.service, group=1)
async def afk_listener(client: Client, message: Message):
    if not message.from_user:
        return

    current_user_id = message.from_user.id

    # 1. Check if the sender was AFK and just returned (IGNORE if they just typed .afk)
    if current_user_id in afk_data:
        text_lower = (message.text or "").strip().lower()
        if not text_lower.startswith((".afk", "/afk")):
            user_info = afk_data.pop(current_user_id)
            elapsed_seconds = int(time.time() - user_info["time"])
            duration_str = get_readable_time(elapsed_seconds)

            user_name = html.escape(message.from_user.first_name or "User")
            mention = f"<a href='tg://user?id={current_user_id}'>{user_name}</a>"

            welcome_back_text = (
                "<blockquote>🌸 <b>𝙒𝙚𝙡𝙘𝙤𝙢𝙚 𝘽𝙖𝙘𝙠</b> 💖\n"
                "✦ ━━━━━━━━━━━━━━━━━━ ✦\n"
                f"👋 Hey {mention}, aap wapas aa gaye!\n"
                f"⏳ <b>Aap offline rahe:</b> <code>{duration_str}</code>\n"
                "✨ <i>AFK status has been removed!</i></blockquote>"
            )
            return await message.reply_text(welcome_back_text, parse_mode=ParseMode.HTML)

    # 2. Check if sender replied to someone who is AFK
    if message.reply_to_message and message.reply_to_message.from_user:
        replied_user_id = message.reply_to_message.from_user.id
        if replied_user_id in afk_data and replied_user_id != current_user_id:
            info = afk_data[replied_user_id]
            elapsed_seconds = int(time.time() - info["time"])
            duration_str = get_readable_time(elapsed_seconds)

            r_name = html.escape(message.reply_to_message.from_user.first_name or "User")
            r_mention = f"<a href='tg://user?id={replied_user_id}'>{r_name}</a>"

            notify_text = (
                "<blockquote>⚠️ <b>𝙐𝙨𝙚𝙧 𝙞𝙨 𝘾𝙪𝙧𝙧𝙚𝙣𝙩𝙡𝙮 𝘼𝙁𝙆!</b> 💤\n"
                "✦ ━━━━━━━━━━━━━━━━━━ ✦\n"
                f"👤 <b>User:</b> {r_mention}\n"
                f"📝 <b>Reason:</b> <i>{html.escape(info['reason'])}</i>\n"
                f"⏳ <b>Since:</b> <code>{duration_str} ago</code></blockquote>"
            )
            return await message.reply_text(notify_text, parse_mode=ParseMode.HTML)

    # 3. Check if someone mentioned an AFK user in text
    if message.entities:
        for ent in message.entities:
            target_id = None
            if ent.type == MessageEntityType.TEXT_MENTION and ent.user:
                target_id = ent.user.id
            elif ent.type == MessageEntityType.MENTION and message.text:
                username_token = message.text[ent.offset : ent.offset + ent.length].lstrip("@")
                for u_id in afk_data:
                    # Match user by checking stored pyrogram users or ID
                    pass

            if target_id and target_id in afk_data and target_id != current_user_id:
                info = afk_data[target_id]
                elapsed_seconds = int(time.time() - info["time"])
                duration_str = get_readable_time(elapsed_seconds)

                t_name = html.escape(ent.user.first_name or "User")
                t_mention = f"<a href='tg://user?id={target_id}'>{t_name}</a>"

                notify_text = (
                    "<blockquote>⚠️ <b>𝙐𝙨𝙚𝙧 𝙞𝙨 𝘾𝙪𝙧𝙧𝙚𝙣𝙩𝙡𝙮 𝘼𝙁𝙆!</b> 💤\n"
                    "✦ ━━━━━━━━━━━━━━━━━━ ✦\n"
                    f"👤 <b>User:</b> {t_mention}\n"
                    f"📝 <b>Reason:</b> <i>{html.escape(info['reason'])}</i>\n"
                    f"⏳ <b>Since:</b> <code>{duration_str} ago</code></blockquote>"
                )
                return await message.reply_text(notify_text, parse_mode=ParseMode.HTML)
                
