import re
from pyrogram import Client, filters
from pyrogram.enums import ParseMode, ChatMemberStatus
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, ChatMemberUpdated

welcome_data = {}

DEFAULT_WELCOME = (
    "<blockquote expandable>✨ <b>𝙬𝙚𝙡𝙘𝙤𝙢𝙚 𝙩𝙤 𝙩𝙝𝙚 𝙜𝙧𝙤𝙪𝙥</b> ✨\n"
    "✦ ━━━━━━━━━━━━━━━━━━ ✦\n"
    "👋 Hello {mention}!\n"
    "🎉 Welcome to <b>{chat}</b>!\n"
    "💬 Group rules follow karein aur chill karein!</blockquote>"
)

async def is_admin(client: Client, user_id: int, chat_id: int) -> bool:
    try:
        member = await client.get_chat_member(chat_id, user_id)
        return member.status.name in ["OWNER", "ADMINISTRATOR"]
    except Exception:
        return False

def parse_buttons_and_clean_text(raw_text: str):
    if not raw_text:
        return "", None

    pattern = r"\[([^\[\]]+)\]\((?:buttonurl:)?\s*(https?://[^\s\)]+)\)|\[([^\[\]]+?)\|(?:\s*)(https?://[^\s]+)\]"
    buttons = []
    lines = raw_text.split("\n")
    cleaned_lines = []

    for line in lines:
        matches = re.findall(pattern, line)
        if matches:
            row = []
            for match in matches:
                text = match[0] if match[0] else match[2]
                url = match[1] if match[1] else match[3]
                row.append(InlineKeyboardButton(text=text.strip(), url=url.strip()))
            if row:
                buttons.append(row)
        else:
            cleaned_lines.append(line)

    cleaned_text = "\n".join(cleaned_lines).rstrip()
    keyboard = InlineKeyboardMarkup(buttons) if buttons else None
    return cleaned_text, keyboard

def format_exact_quotes(html_text: str) -> str:
    if not html_text:
        return ""
    cleaned = re.sub(r'<blockquote[^>]*>', '<blockquote>', html_text)
    return re.sub(r'<blockquote>', '<blockquote expandable>', cleaned, count=1)

def apply_template_tags(template: str, user, chat_title: str) -> str:
    first_name = user.first_name or "Member"
    last_name = user.last_name or ""
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

async def send_custom_welcome(client: Client, chat_id: int, user, chat_title: str):
    settings = welcome_data.get(chat_id, {"enabled": True, "type": "text", "file_id": None, "text": DEFAULT_WELCOME, "keyboard": None})

    if not settings.get("enabled", True):
        return

    raw_template = settings.get("text", DEFAULT_WELCOME)
    keyboard = settings.get("keyboard")
    m_type = settings.get("type", "text")
    f_id = settings.get("file_id")

    formatted_text = apply_template_tags(raw_template, user, chat_title)

    try:
        if m_type == "photo" and f_id:
            await client.send_photo(chat_id=chat_id, photo=f_id, caption=formatted_text, reply_markup=keyboard, parse_mode=ParseMode.HTML)
        elif m_type == "video" and f_id:
            await client.send_video(chat_id=chat_id, video=f_id, caption=formatted_text, reply_markup=keyboard, parse_mode=ParseMode.HTML)
        elif m_type == "animation" and f_id:
            await client.send_animation(chat_id=chat_id, animation=f_id, caption=formatted_text, reply_markup=keyboard, parse_mode=ParseMode.HTML)
        else:
            await client.send_message(chat_id=chat_id, text=formatted_text, reply_markup=keyboard, parse_mode=ParseMode.HTML, disable_web_page_preview=True)
    except Exception:
        pass

# ==================== .setwelcome ====================
@Client.on_message(filters.command(["setwelcome"], prefixes=[".", "/"]) & filters.group)
async def set_welcome_msg(client: Client, message: Message):
    if not message.from_user or not await is_admin(client, message.from_user.id, message.chat.id):
        return

    chat_id = message.chat.id
    reply = message.reply_to_message

    media_type = "text"
    file_id = None
    target_text = None
    custom_keyboard = None

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

        if reply.reply_markup and reply.reply_markup.inline_keyboard:
            custom_keyboard = reply.reply_markup
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
    final_keyboard = custom_keyboard or parsed_keyboard

    welcome_data[chat_id] = {
        "enabled": True,
        "type": media_type,
        "file_id": file_id,
        "text": final_text,
        "keyboard": final_keyboard
    }

    admin_name = message.from_user.first_name or "Admin"
    preview = (
        "<blockquote>🎉 <b>𝙬𝙚𝙡𝙘𝙤𝙢𝙚 𝙢𝙚𝙨𝙨𝙖𝙜𝙚 𝙨𝙚𝙩</b> 🎉\n"
        "✦ ━━━━━━━━━━━━━━━━━━ ✦\n"
        f"👮 <b>Set By:</b> <a href='tg://user?id={message.from_user.id}'>{admin_name}</a>\n"
        "⚡ <b>Status:</b> Cleanservice support & tags active!</blockquote>"
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
        welcome_data[chat_id] = {"enabled": True, "type": "text", "file_id": None, "text": DEFAULT_WELCOME, "keyboard": None}

    admin_name = message.from_user.first_name or "Admin"

    if mode in ["on", "enable", "chalu"]:
        welcome_data[chat_id]["enabled"] = True
        await message.reply_text(
            f"<blockquote>🟢 <b>Greetings Enabled by <a href='tg://user?id={message.from_user.id}'>{admin_name}</a>!</b></blockquote>",
            parse_mode=ParseMode.HTML
        )
    elif mode in ["off", "disable", "band"]:
        welcome_data[chat_id]["enabled"] = False
        await message.reply_text(
            f"<blockquote>🔴 <b>Greetings Disabled by <a href='tg://user?id={message.from_user.id}'>{admin_name}</a>!</b></blockquote>",
            parse_mode=ParseMode.HTML
        )

# ==================== .getwelcome & .resetwelcome ====================
@Client.on_message(filters.command(["getwelcome"], prefixes=[".", "/"]) & filters.group)
async def get_welcome_cmd(client: Client, message: Message):
    if not message.from_user or not await is_admin(client, message.from_user.id, message.chat.id):
        return
    curr = welcome_data.get(message.chat.id, {"type": "text", "file_id": None, "text": DEFAULT_WELCOME, "keyboard": None})
    m_type = curr.get("type", "text")
    f_id = curr.get("file_id")
    txt = curr.get("text", DEFAULT_WELCOME)
    kb = curr.get("keyboard")

    if m_type == "photo" and f_id:
        await message.reply_photo(photo=f_id, caption=txt, reply_markup=kb, parse_mode=ParseMode.HTML)
    elif m_type == "video" and f_id:
        await message.reply_video(video=f_id, caption=txt, reply_markup=kb, parse_mode=ParseMode.HTML)
    elif m_type == "animation" and f_id:
        await message.reply_animation(animation=f_id, caption=txt, reply_markup=kb, parse_mode=ParseMode.HTML)
    else:
        await message.reply_text(text=txt, reply_markup=kb, parse_mode=ParseMode.HTML, disable_web_page_preview=True)

@Client.on_message(filters.command(["resetwelcome"], prefixes=[".", "/"]) & filters.group)
async def reset_welcome_cmd(client: Client, message: Message):
    if not message.from_user or not await is_admin(client, message.from_user.id, message.chat.id):
        return
    welcome_data[message.chat.id] = {"enabled": True, "type": "text", "file_id": None, "text": DEFAULT_WELCOME, "keyboard": None}
    await message.reply_text("<blockquote>🔄 <b>Welcome message reset to default!</b></blockquote>", parse_mode=ParseMode.HTML)

# ==================== Member Join Handlers (Detects Cleanservice & Joins) ====================

# 1. ChatMemberUpdated: Triggers even if cleanservice deletes service messages or user joins via link / request
@Client.on_chat_member_updated()
async def member_status_update(client: Client, update: ChatMemberUpdated):
    # Member join hua ya approve hua
    old_status = update.old_chat_member.status if update.old_chat_member else None
    new_status = update.new_chat_member.status if update.new_chat_member else None

    # Check if user transitioned from left/kicked/restricted to member
    if old_status in [None, ChatMemberStatus.LEFT, ChatMemberStatus.BANNED] and new_status == ChatMemberStatus.MEMBER:
        bot = await client.get_me()
        user = update.new_chat_member.user
        if user.id == bot.id:
            return
        chat_title = update.chat.title or "Group"
        await send_custom_welcome(client, update.chat.id, user, chat_title)

# 2. Normal service message fallback
@Client.on_message(filters.new_chat_members & filters.group)
async def welcome_new_member_msg(client: Client, message: Message):
    bot = await client.get_me()
    for user in message.new_chat_members:
        if user.id == bot.id:
            continue
        chat_title = message.chat.title or "Group"
        await send_custom_welcome(client, message.chat.id, user, chat_title)
        
