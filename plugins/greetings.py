import os
import json
import asyncio
import urllib.request
import re
from pyrogram import Client, filters
from pyrogram.enums import ParseMode, ChatMemberStatus
from pyrogram.types import Message, ChatMemberUpdated

welcome_data = {}

DEFAULT_WELCOME = (
    "<blockquote expandable>✨ <b>𝙬𝙚𝙡𝙘𝙤𝙢𝙚 𝙩𝙤 𝙩𝙝𝙚 𝙜𝙧𝙤𝙪𝙥</b> ✨\n"
    "✦ ━━━━━━━━━━━━━━━━━━ ✦\n"
    "👋 Hello {mention}!\n"
    "🎉 Welcome to <b>{chat}</b>!\n"
    "💬 Group rules follow karein aur chill karein!</blockquote>"
)

def get_token():
    return os.environ.get("BOT_TOKEN", "").strip().strip('"').strip("'")

# Pure Telegram Bot API 9.4 HTTP Engine
async def call_tg_bot_api(endpoint: str, payload: dict):
    token = get_token()
    if not token:
        return None

    url = f"https://api.telegram.org/bot{token}/{endpoint}"
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})

    def _sync():
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as he:
            err = he.read().decode("utf-8", errors="ignore")
            print(f"[BotAPI HTTP {he.code}] {err}")
            return None
        except Exception as e:
            print(f"[BotAPI Conn Error] {e}")
            return None

    return await asyncio.to_thread(_sync)

async def is_admin(client: Client, user_id: int, chat_id: int) -> bool:
    try:
        member = await client.get_chat_member(chat_id, user_id)
        return member.status.name in ["OWNER", "ADMINISTRATOR"]
    except Exception:
        return False

# Telegram Bot API 9.4 Styles: primary = Blue, danger = Red, success = Green
PALETTE_STYLES = ["primary", "danger", "success"]

def parse_buttons(raw_text: str):
    if not raw_text:
        return "", None

    # Matches: [Title](buttonurl:https://...) or [Title | https://...]
    btn_regex = re.compile(
        r"\[([^\[\]\(\)\|]+)\](?:\((?:buttonurl:)?\s*(https?://[^\s\)]+)\)|\|\s*(https?://[^\[\]\|\s]+)(?:\s*\|\s*([a-zA-Z]+))?\]?)"
    )

    buttons = []
    lines = raw_text.split("\n")
    cleaned_lines = []
    btn_idx = 0

    for line in lines:
        if "[" in line and "http" in line:
            matches = btn_regex.findall(line)
            if matches:
                row = []
                for m in matches:
                    title = m[0].strip()
                    url = m[1].strip() if m[1] else m[2].strip()
                    custom_color = (m[3] or "").strip().lower()

                    if custom_color in ["blue", "primary"]:
                        style = "primary"
                    elif custom_color in ["red", "danger"]:
                        style = "danger"
                    elif custom_color in ["green", "success"]:
                        style = "success"
                    else:
                        style = PALETTE_STYLES[btn_idx % len(PALETTE_STYLES)]
                        btn_idx += 1

                    # Remove any extra emoji user typed, so only button text with Bot API color renders
                    cleaned_title = re.sub(r'^[🔵🔴🟢]\s*', '', title)

                    row.append({
                        "text": cleaned_title,
                        "url": url,
                        "style": style
                    })
                if row:
                    buttons.append(row)
                    continue

        cleaned_lines.append(line)

    cleaned_text = "\n".join(cleaned_lines).rstrip()
    keyboard = {"inline_keyboard": buttons} if buttons else None
    return cleaned_text, keyboard

def format_exact_quotes(html_text: str) -> str:
    if not html_text:
        return ""
    if "<blockquote" not in html_text:
        return f"<blockquote expandable>{html_text}</blockquote>"
    cleaned = re.sub(r'<blockquote[^>]*>', '<blockquote>', html_text)
    return re.sub(r'<blockquote>', '<blockquote expandable>', cleaned, count=1)

def apply_template_tags(template: str, user, chat_title: str) -> str:
    first_name = (user.first_name or "Member").replace("<", "").replace(">", "")
    last_name = (user.last_name or "").replace("<", "").replace(">", "")
    full_name = f"{first_name} {last_name}".strip()
    mention = f"<a href='tg://user?id={user.id}'>{first_name}</a>"
    username = f"@{user.username}" if user.username else mention

    replacements = {
        "{first}": mention,
        "{name}": mention,
        "{fullname}": f"<a href='tg://user?id={user.id}'>{full_name}</a>",
        "{mention}": mention,
        "{username}": username,
        "{id}": str(user.id),
        "{chat}": chat_title,
        "{title}": chat_title
    }

    res = template
    for key, val in replacements.items():
        res = re.sub(re.escape(key), val, res, flags=re.IGNORECASE)
    return res

async def send_welcome_payload(client: Client, chat_id: int, user, chat_title: str):
    settings = welcome_data.get(chat_id, {
        "enabled": True,
        "type": "text",
        "file_id": None,
        "text": DEFAULT_WELCOME,
        "keyboard": None
    })

    if not settings.get("enabled", True):
        return

    raw_template = settings.get("text") or DEFAULT_WELCOME
    keyboard = settings.get("keyboard")
    m_type = settings.get("type", "text")
    f_id = settings.get("file_id")

    caption = apply_template_tags(raw_template, user, chat_title)

    payload = {
        "chat_id": chat_id,
        "parse_mode": "HTML"
    }
    if keyboard:
        payload["reply_markup"] = keyboard

    # 1. Video / Animation
    if m_type in ["video", "animation"] and f_id:
        payload["video"] = f_id
        payload["caption"] = caption
        res = await call_tg_bot_api("sendVideo", payload)
        if not (res and res.get("ok")):
            payload.pop("video", None)
            payload["animation"] = f_id
            res = await call_tg_bot_api("sendAnimation", payload)
        if res and res.get("ok"):
            return

    # 2. Photo
    elif m_type == "photo" and f_id:
        payload["photo"] = f_id
        payload["caption"] = caption
        res = await call_tg_bot_api("sendPhoto", payload)
        if res and res.get("ok"):
            return

    # 3. Text Message
    elif m_type == "text" or not f_id:
        payload["text"] = caption
        payload["disable_web_page_preview"] = True
        res = await call_tg_bot_api("sendMessage", payload)
        if res and res.get("ok"):
            return

    # Fallback to copy_message (guarantees buttons attach to original media)
    saved_msg_id = settings.get("message_id")
    if saved_msg_id:
        try:
            from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
            fallback_buttons = [
                [InlineKeyboardButton(text=b["text"], url=b["url"]) for b in row]
                for row in keyboard["inline_keyboard"]
            ] if keyboard else None

            await client.copy_message(
                chat_id=chat_id,
                from_chat_id=chat_id,
                message_id=saved_msg_id,
                caption=caption,
                parse_mode=ParseMode.HTML,
                reply_markup=InlineKeyboardMarkup(fallback_buttons) if fallback_buttons else None
            )
        except Exception as e:
            print(f"[Copy fallback error]: {e}")

# ==================== .setwelcome ====================
@Client.on_message(filters.command(["setwelcome"], prefixes=[".", "/"]) & filters.group)
async def set_welcome_msg(client: Client, message: Message):
    if not message.from_user or not await is_admin(client, message.from_user.id, message.chat.id):
        return

    chat_id = message.chat.id
    reply = message.reply_to_message

    media_type = "text"
    file_id = None
    target_text = ""
    saved_message_id = None

    if reply:
        saved_message_id = reply.id
        if reply.video:
            media_type = "video"
            file_id = reply.video.file_id
            target_text = reply.caption.html if reply.caption else ""
        elif reply.animation:
            media_type = "animation"
            file_id = reply.animation.file_id
            target_text = reply.caption.html if reply.caption else ""
        elif reply.photo:
            media_type = "photo"
            file_id = reply.photo.file_id
            target_text = reply.caption.html if reply.caption else ""
        else:
            media_type = "text"
            target_text = reply.text.html if reply.text else ""
    else:
        parts = message.text.html.split(maxsplit=1)
        if len(parts) > 1:
            target_text = parts[1]

    if not target_text and not file_id:
        return await message.reply_text(
            "<blockquote>⚠️ <b>Kisi video ya message par reply karke <code>.setwelcome</code> likhein.</b></blockquote>",
            parse_mode=ParseMode.HTML
        )

    cleaned_text, parsed_keyboard = parse_buttons(target_text)
    final_text = format_exact_quotes(cleaned_text)

    welcome_data[chat_id] = {
        "enabled": True,
        "type": media_type,
        "file_id": file_id,
        "message_id": saved_message_id,
        "text": final_text,
        "keyboard": parsed_keyboard
    }

    admin_name = message.from_user.first_name or "Admin"
    btn_count = sum(len(r) for r in parsed_keyboard["inline_keyboard"]) if parsed_keyboard else 0

    preview = (
        "<blockquote>🎉 <b>𝙬𝙚𝙡𝙘𝙤𝙢𝙚 𝙢𝙚𝙨𝙨𝙖𝙜𝙚 𝙨𝙚𝙩</b> 🎉\n"
        "✦ ━━━━━━━━━━━━━━━━━━ ✦\n"
        f"👮 <b>Set By:</b> <a href='tg://user?id={message.from_user.id}'>{admin_name}</a>\n"
        f"🎬 <b>Media:</b> <code>{media_type.upper()}</code>\n"
        f"🎨 <b>Buttons Configured:</b> <code>{btn_count} Buttons (Bot API 9.4 Colors Applied)</code>\n"
        "⚡ <b>Status:</b> Saved Successfully!</blockquote>"
    )
    await message.reply_text(preview, parse_mode=ParseMode.HTML)

# ==================== .welcome on / off ====================
@Client.on_message(filters.command(["welcome"], prefixes=[".", "/"]) & filters.group)
async def toggle_welcome(client: Client, message: Message):
    if not message.from_user or not await is_admin(client, message.from_user.id, message.chat.id):
        return

    chat_id = message.chat.id
    args = message.text.split()

    if len(args) < 2:
        is_on = welcome_data.get(chat_id, {}).get("enabled", True)
        curr = "ON 🟢" if is_on else "OFF 🔴"
        return await message.reply_text(
            f"<blockquote>ℹ️ <b>Greetings Status:</b> <code>{curr}</code>\n"
            "Use: <code>.welcome on</code> ya <code>.welcome off</code></blockquote>",
            parse_mode=ParseMode.HTML
        )

    mode = args[1].lower()
    if chat_id not in welcome_data:
        welcome_data[chat_id] = {"enabled": True, "type": "text", "file_id": None, "message_id": None, "text": DEFAULT_WELCOME, "keyboard": None}

    admin_name = message.from_user.first_name or "Admin"

    if mode in ["on", "enable", "chalu"]:
        welcome_data[chat_id]["enabled"] = True
        await message.reply_text(f"<blockquote>🟢 <b>Greetings Enabled by {admin_name}!</b></blockquote>", parse_mode=ParseMode.HTML)
    elif mode in ["off", "disable", "band"]:
        welcome_data[chat_id]["enabled"] = False
        await message.reply_text(f"<blockquote>🔴 <b>Greetings Disabled by {admin_name}!</b></blockquote>", parse_mode=ParseMode.HTML)

# ==================== .getwelcome & .resetwelcome ====================
@Client.on_message(filters.command(["getwelcome"], prefixes=[".", "/"]) & filters.group)
async def get_welcome_cmd(client: Client, message: Message):
    if not message.from_user or not await is_admin(client, message.from_user.id, message.chat.id):
        return
    await send_welcome_payload(client, message.chat.id, message.from_user, message.chat.title or "Group")

@Client.on_message(filters.command(["resetwelcome"], prefixes=[".", "/"]) & filters.group)
async def reset_welcome_cmd(client: Client, message: Message):
    if not message.from_user or not await is_admin(client, message.from_user.id, message.chat.id):
        return
    welcome_data[message.chat.id] = {"enabled": True, "type": "text", "file_id": None, "message_id": None, "text": DEFAULT_WELCOME, "keyboard": None}
    await message.reply_text("<blockquote>🔄 <b>Welcome message reset to default!</b></blockquote>", parse_mode=ParseMode.HTML)

# ==================== Member Join Handlers ====================
@Client.on_chat_member_updated()
async def member_status_update(client: Client, update: ChatMemberUpdated):
    old_status = update.old_chat_member.status if update.old_chat_member else None
    new_status = update.new_chat_member.status if update.new_chat_member else None

    if old_status in [None, ChatMemberStatus.LEFT, ChatMemberStatus.BANNED] and new_status == ChatMemberStatus.MEMBER:
        bot = await client.get_me()
        user = update.new_chat_member.user
        if user.id == bot.id:
            return
        chat_title = update.chat.title or "Group"
        await send_welcome_payload(client, update.chat.id, user, chat_title)

@Client.on_message(filters.new_chat_members & filters.group)
async def welcome_new_member_msg(client: Client, message: Message):
    bot = await client.get_me()
    for user in message.new_chat_members:
        if user.id == bot.id:
            continue
        chat_title = message.chat.title or "Group"
        await send_welcome_payload(client, message.chat.id, user, chat_title)
    
