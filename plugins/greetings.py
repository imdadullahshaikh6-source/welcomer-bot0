import re
from pyrogram import Client, filters
from pyrogram.enums import ParseMode
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

# Stores: {chat_id: {"enabled": bool, "type": str, "file_id": str, "text": str, "keyboard": InlineKeyboardMarkup}}
welcome_data = {}

DEFAULT_WELCOME = (
    "<blockquote>✨ <b>𝙬𝙚𝙡𝙘𝙤𝙢𝙚 𝙩𝙤 𝙩𝙝𝙚 𝙜𝙧𝙤𝙪𝙥</b> ✨\n"
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
    """
    Parses both button formats:
    1) [Text](buttonurl:https://...)
    2) [Text | https://...]
    """
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
                # Group 0 & 1 for markdown buttonurl, Group 2 & 3 for pipe format
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
        # Detect media
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

        # Capture reply markup if already has inline buttons
        if reply.reply_markup and reply.reply_markup.inline_keyboard:
            custom_keyboard = reply.reply_markup
    else:
        parts = message.text.html.split(maxsplit=1)
        if len(parts) > 1:
            target_text = parts[1]

    if not target_text and not file_id:
        help_txt = (
            "<blockquote>⚠️ <b>Format dekhein:</b>\n\n"
            "Photo, Video ya kisi message par reply karke <code>.setwelcome</code> likhein.\n\n"
            "<b>Supported Button Formats:</b>\n"
            "• <code>[Music](buttonurl:https://t.me/...)</code>\n"
            "• <code>[Help | https://t.me/...]</code>\n\n"
            "<b>Tags:</b> <code>{mention}</code>, <code>{name}</code>, <code>{chat}</code>, <code>{id}</code></blockquote>"
        )
        return await message.reply_text(help_txt, parse_mode=ParseMode.HTML)

    # Parse buttons from text if not attached directly to message
    cleaned_text, parsed_keyboard = parse_buttons_and_clean_text(target_text)
    final_keyboard = custom_keyboard or parsed_keyboard

    welcome_data[chat_id] = {
        "enabled": True,
        "type": media_type,
        "file_id": file_id,
        "text": cleaned_text,
        "keyboard": final_keyboard
    }

    admin_name = message.from_user.first_name or "Admin"
    preview = (
        "<blockquote>🎉 <b>𝙬𝙚𝙡𝙘𝙤𝙢𝙚 𝙢𝙚𝙨𝙨𝙖𝙜𝙚 𝙨𝙚𝙩</b> 🎉\n"
        "✦ ━━━━━━━━━━━━━━━━━━ ✦\n"
        f"👮 <b>Set By:</b> <a href='tg://user?id={message.from_user.id}'>{admin_name}</a>\n"
        f"🖼️ <b>Media:</b> <code>{media_type.capitalize()}</code>\n"
        f"🔘 <b>Buttons:</b> <code>{'Found' if final_keyboard else 'None'}</code>\n"
        "⚡ <b>Status:</b> All quotes, custom fonts & media successfully saved!</blockquote>"
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

# ==================== Member Join Event ====================
@Client.on_message(filters.new_chat_members & filters.group)
async def welcome_new_member(client: Client, message: Message):
    chat_id = message.chat.id
    settings = welcome_data.get(chat_id, {"enabled": True, "type": "text", "file_id": None, "text": DEFAULT_WELCOME, "keyboard": None})

    if not settings.get("enabled", True):
        return

    bot = await client.get_me()
    for user in message.new_chat_members:
        if user.id == bot.id:
            continue

        raw_template = settings.get("text", DEFAULT_WELCOME)
        keyboard = settings.get("keyboard")
        m_type = settings.get("type", "text")
        f_id = settings.get("file_id")

        first_name = user.first_name or "Member"
        mention = f"<a href='tg://user?id={user.id}'>{first_name}</a>"
        chat_title = message.chat.title or "Group"

        # Replace tags
        formatted_text = (
            raw_template
            .replace("{mention}", mention)
            .replace("{name}", first_name)
            .replace("{chat}", chat_title)
            .replace("{id}", str(user.id))
        )

        try:
            if m_type == "photo" and f_id:
                await message.reply_photo(photo=f_id, caption=formatted_text, reply_markup=keyboard, parse_mode=ParseMode.HTML)
            elif m_type == "video" and f_id:
                await message.reply_video(video=f_id, caption=formatted_text, reply_markup=keyboard, parse_mode=ParseMode.HTML)
            elif m_type == "animation" and f_id:
                await message.reply_animation(animation=f_id, caption=formatted_text, reply_markup=keyboard, parse_mode=ParseMode.HTML)
            else:
                await message.reply_text(text=formatted_text, reply_markup=keyboard, parse_mode=ParseMode.HTML, disable_web_page_preview=True)
        except Exception:
            pass
