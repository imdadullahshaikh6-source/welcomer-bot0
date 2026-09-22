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

# Standard Bot API JSON Call
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
            print(f"[BotAPI Error] {e}")
            return None

    return await asyncio.to_thread(_sync)

# Multipart Upload for Photos/Media so Bot API gets native file & styles
async def upload_tg_bot_api(endpoint: str, fields: dict, file_field: str, filename: str, file_data: bytes):
    token = get_token()
    if not token:
        return None

    boundary = "----WebKitFormBoundary7MA4YWxkTrZu0gW"
    body = bytearray()

    for key, val in fields.items():
        if val is None:
            continue
        body.extend(f"--{boundary}\r\n".encode())
        body.extend(f'Content-Disposition: form-data; name="{key}"\r\n\r\n'.encode())
        body.extend(f"{val}\r\n".encode())

    body.extend(f"--{boundary}\r\n".encode())
    body.extend(f'Content-Disposition: form-data; name="{file_field}"; filename="{filename}"\r\n'.encode())
    body.extend(b"Content-Type: application/octet-stream\r\n\r\n")
    body.extend(file_data)
    body.extend(b"\r\n")
    body.extend(f"--{boundary}--\r\n".encode())

    url = f"https://api.telegram.org/bot{token}/{endpoint}"
    req = urllib.request.Request(url, data=bytes(body), headers={"Content-Type": f"multipart/form-data; boundary={boundary}"})

    def _sync():
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except Exception as e:
            print(f"[BotAPI Multipart Error] {e}")
            return None

    return await asyncio.to_thread(_sync)

async def is_admin(client: Client, user_id: int, chat_id: int) -> bool:
    try:
        member = await client.get_chat_member(chat_id, user_id)
        return member.status.name in ["OWNER", "ADMINISTRATOR"]
    except Exception:
        return False

# Distinct Color Rotation: 1st Blue, 2nd Red, 3rd Green
PALETTE = ["primary", "danger", "success"]

def parse_buttons_and_clean_text(raw_text: str):
    if not raw_text:
        return "", None

    buttons = []
    lines = raw_text.split("\n")
    cleaned_lines = []
    button_counter = 0

    btn_regex = re.compile(
        r"\[([^\[\]\(\)]+?)\](?:\((?:buttonurl:)?\s*(https?://[^\s\)]+)\)|(?:\|\s*(https?://[^\[\]\|\s]+)(?:\s*\|\s*([a-zA-Z]+))?))"
    )

    for line in lines:
        matches = btn_regex.findall(line)
        if matches:
            row = []
            for m in matches:
                text = m[0].strip()
                url = m[1].strip() if m[1] else m[2].strip()
                color_raw = (m[3] or "").strip().lower()

                if color_raw in ["blue", "primary"]:
                    style = "primary"
                elif color_raw in ["red", "danger"]:
                    style = "danger"
                elif color_raw in ["green", "success"]:
                    style = "success"
                else:
                    # Alternating colors: each button gets a unique distinct color!
                    style = PALETTE[button_counter % len(PALETTE)]
                    button_counter += 1

                row.append({"text": text, "url": url, "style": style})
            if row:
                buttons.append(row)
        else:
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
        "bot_api_file_id": None,
        "text": DEFAULT_WELCOME,
        "keyboard": None
    })

    if not settings.get("enabled", True):
        return

    raw_template = settings.get("text") or DEFAULT_WELCOME
    keyboard = settings.get("keyboard")
    m_type = settings.get("type", "text")
    f_id = settings.get("file_id")
    bot_api_f_id = settings.get("bot_api_file_id")

    formatted_text = apply_template_tags(raw_template, user, chat_title)

    payload = {"chat_id": chat_id, "parse_mode": "HTML"}
    if keyboard:
        payload["reply_markup"] = keyboard

    # 1. If Photo with cached Bot API file_id
    if m_type == "photo":
        if bot_api_f_id:
            payload["photo"] = bot_api_f_id
            payload["caption"] = formatted_text
            res = await call_tg_bot_api("sendPhoto", payload)
            if res and res.get("ok"):
                return
        # If Bot API file_id is not yet cached, download via Pyrogram & upload to Bot API
        elif f_id:
            try:
                dl_path = await client.download_media(f_id)
                if dl_path and os.path.exists(dl_path):
                    with open(dl_path, "rb") as f:
                        f_bytes = f.read()
                    try:
                        os.remove(dl_path)
                    except Exception:
                        pass
                    
                    fields = {
                        "chat_id": str(chat_id),
                        "caption": formatted_text,
                        "parse_mode": "HTML"
                    }
                    if keyboard:
                        fields["reply_markup"] = json.dumps(keyboard)

                    res = await upload_tg_bot_api("sendPhoto", fields, "photo", "welcome.jpg", f_bytes)
                    if res and res.get("ok"):
                        # Cache the Bot API file_id for all future requests
                        welcome_data[chat_id]["bot_api_file_id"] = res["result"]["photo"][-1]["file_id"]
                        return
            except Exception as e:
                print(f"[Download/Upload fallback error]: {e}")

    # 2. Text Message
    elif m_type == "text":
        payload["text"] = formatted_text
        payload["disable_web_page_preview"] = True
        res = await call_tg_bot_api("sendMessage", payload)
        if res and res.get("ok"):
            return

    # 3. Bulletproof Fallback via Pyrogram so message NEVER gets dropped
    from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    fallback_markup = None
    if keyboard and "inline_keyboard" in keyboard:
        fallback_rows = []
        for row in keyboard["inline_keyboard"]:
            fallback_rows.append([InlineKeyboardButton(text=btn["text"], url=btn["url"]) for btn in row if "url" in btn])
        if any(fallback_rows):
            fallback_markup = InlineKeyboardMarkup(fallback_rows)

    if m_type == "photo" and f_id:
        await client.send_photo(chat_id=chat_id, photo=f_id, caption=formatted_text, parse_mode=ParseMode.HTML, reply_markup=fallback_markup)
    else:
        await client.send_message(chat_id=chat_id, text=formatted_text, parse_mode=ParseMode.HTML, disable_web_page_preview=True, reply_markup=fallback_markup)

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

    if reply:
        if reply.photo:
            media_type = "photo"
            file_id = reply.photo.file_id
            target_text = reply.caption.html if reply.caption else ""
        elif reply.video:
            media_type = "video"
            file_id = reply.video.file_id
            target_text = reply.caption.html if reply.caption else ""
        elif reply.animation:
            media_type = "animation"
            file_id = reply.animation.file_id
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
            "<blockquote>⚠️ <b>Kisi message/media par reply karke <code>.setwelcome</code> likhein.</b></blockquote>",
            parse_mode=ParseMode.HTML
        )

    cleaned_text, parsed_keyboard = parse_buttons_and_clean_text(target_text)
    final_text = format_exact_quotes(cleaned_text)

    # Immediately cache downloaded bytes and upload to Bot API to obtain real Bot API file_id
    bot_api_file_id = None
    if media_type == "photo" and reply and reply.photo:
        try:
            dl_path = await client.download_media(reply.photo)
            if dl_path and os.path.exists(dl_path):
                with open(dl_path, "rb") as f:
                    f_bytes = f.read()
                try:
                    os.remove(dl_path)
                except Exception:
                    pass

                fields = {
                    "chat_id": str(chat_id),
                    "caption": "<blockquote>✨ <b>Preview Welcome Message</b></blockquote>",
                    "parse_mode": "HTML"
                }
                if parsed_keyboard:
                    fields["reply_markup"] = json.dumps(parsed_keyboard)

                test_res = await upload_tg_bot_api("sendPhoto", fields, "photo", "welcome.jpg", f_bytes)
                if test_res and test_res.get("ok"):
                    bot_api_file_id = test_res["result"]["photo"][-1]["file_id"]
        except Exception as e:
            print(f"[Initial Media Upload Error]: {e}")

    welcome_data[chat_id] = {
        "enabled": True,
        "type": media_type,
        "file_id": file_id,
        "bot_api_file_id": bot_api_file_id,
        "text": final_text,
        "keyboard": parsed_keyboard
    }

    admin_name = message.from_user.first_name or "Admin"
    preview = (
        "<blockquote>🎉 <b>𝙬𝙚𝙡𝙘𝙤𝙢𝙚 𝙢𝙚𝙨𝙨𝙖𝙜𝙚 𝙨𝙚𝙩</b> 🎉\n"
        "✦ ━━━━━━━━━━━━━━━━━━ ✦\n"
        f"👮 <b>Set By:</b> <a href='tg://user?id={message.from_user.id}'>{admin_name}</a>\n"
        "🎨 <b>Buttons:</b> Multi-Color Engine (Blue / Red / Green) Ready!\n"
        "⚡ <b>Status:</b> Custom Welcome Saved & Verified!</blockquote>"
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
        welcome_data[chat_id] = {"enabled": True, "type": "text", "file_id": None, "bot_api_file_id": None, "text": DEFAULT_WELCOME, "keyboard": None}

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
    welcome_data[message.chat.id] = {"enabled": True, "type": "text", "file_id": None, "bot_api_file_id": None, "text": DEFAULT_WELCOME, "keyboard": None}
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
        
