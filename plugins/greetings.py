import re
from pyrogram import Client, filters
from pyrogram.enums import ParseMode
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

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

def parse_buttons_from_text(text: str):
    """Parses button formats like [Rules | https://t.me/...]"""
    button_regex = r"\[([^\[]+?)\|(?:\s*)(https?://[^\s]+)\]"
    buttons = []
    lines = text.split("\n")
    cleaned_lines = []

    for line in lines:
        matches = re.findall(button_regex, line)
        if matches:
            row = [InlineKeyboardButton(text=m[0].strip(), url=m[1].strip()) for m in matches]
            buttons.append(row)
        else:
            cleaned_lines.append(line)

    cleaned_text = "\n".join(cleaned_lines).strip()
    keyboard = InlineKeyboardMarkup(buttons) if buttons else None
    return cleaned_text, keyboard

# ==================== .setwelcome ====================
@Client.on_message(filters.command(["setwelcome"], prefixes=[".", "/"]) & filters.group)
async def set_welcome_msg(client: Client, message: Message):
    if not message.from_user or not await is_admin(client, message.from_user.id, message.chat.id):
        return

    chat_id = message.chat.id
    target_text = None
    reply = message.reply_to_message

    if reply:
        # Exact HTML format with tags, formatting, entities & emojis
        target_text = reply.text.html if reply.text else (reply.caption.html if reply.caption else None)
        # Inline keyboard capture
        if reply.reply_markup and reply.reply_markup.inline_keyboard:
            welcome_data[chat_id] = {
                "enabled": True,
                "text": target_text,
                "keyboard": reply.reply_markup
            }
            admin_name = message.from_user.first_name or "Admin"
            return await message.reply_text(
                "<blockquote>🎉 <b>𝙬𝙚𝙡𝙘𝙤𝙢𝙚 𝙢𝙚𝙨𝙨𝙖𝙜𝙚 𝙨𝙚𝙩</b> 🎉\n"
                "✦ ━━━━━━━━━━━━━━━━━━ ✦\n"
                f"👮 <b>Set By:</b> <a href='tg://user?id={message.from_user.id}'>{admin_name}</a>\n"
                "⚡ <b>Status:</b> Fonts, quotes, buttons aur emojis ke sath save ho gaya!</blockquote>",
                parse_mode=ParseMode.HTML
            )
    else:
        parts = message.text.html.split(maxsplit=1)
        if len(parts) > 1:
            target_text = parts[1]

    if not target_text:
        help_txt = (
            "<blockquote expandable>⚠️ <b>Welcome Setup Guide:</b>\n\n"
            "Kisi bhi formatted message (fonts/emojis/buttons) par reply karke <code>.setwelcome</code> likhein.\n\n"
            "<b>Supported Tags:</b>\n"
            "• <code>{mention}</code> - User link\n"
            "• <code>{name}</code> - User first name\n"
            "• <code>{chat}</code> - Group name\n"
            "• <code>{id}</code> - User ID\n\n"
            "<b>Collapsible Quote format:</b>\n"
            "<code>&lt;blockquote expandable&gt;Aapka text yahan&lt;/blockquote&gt;</code>\n\n"
            "<b>Button format in text:</b>\n"
            "<code>[Rule Button | https://t.me/...]</code></blockquote>"
        )
        return await message.reply_text(help_txt, parse_mode=ParseMode.HTML)

    cleaned_text, extracted_keyboard = parse_buttons_from_text(target_text)

    welcome_data[chat_id] = {
        "enabled": True,
        "text": cleaned_text,
        "keyboard": extracted_keyboard
    }

    admin_name = message.from_user.first_name or "Admin"
    preview = (
        "<blockquote>🎉 <b>𝙬𝙚𝙡𝙘𝙤𝙢𝙚 𝙢𝙚𝙨𝙨𝙖𝙜𝙚 𝙨𝙚𝙩</b> 🎉\n"
        "✦ ━━━━━━━━━━━━━━━━━━ ✦\n"
        f"👮 <b>Set By:</b> <a href='tg://user?id={message.from_user.id}'>{admin_name}</a>\n"
        "⚡ <b>Status:</b> Fonts, expandable quotes aur buttons save ho chuke hain!</blockquote>"
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
        welcome_data[chat_id] = {"enabled": True, "text": DEFAULT_WELCOME, "keyboard": None}

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
    else:
        await message.reply_text("<blockquote>⚠️ Use: <code>.welcome on</code> ya <code>.welcome off</code></blockquote>", parse_mode=ParseMode.HTML)

# ==================== .getwelcome & .resetwelcome ====================
@Client.on_message(filters.command(["getwelcome"], prefixes=[".", "/"]) & filters.group)
async def get_welcome_cmd(client: Client, message: Message):
    if not message.from_user or not await is_admin(client, message.from_user.id, message.chat.id):
        return
    curr_data = welcome_data.get(message.chat.id, {"text": DEFAULT_WELCOME, "keyboard": None})
    template = curr_data.get("text", DEFAULT_WELCOME)
    keyboard = curr_data.get("keyboard")
    await message.reply_text(
        f"<b>Current Welcome Template:</b>\n\n{template}",
        reply_markup=keyboard,
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True
    )

@Client.on_message(filters.command(["resetwelcome"], prefixes=[".", "/"]) & filters.group)
async def reset_welcome_cmd(client: Client, message: Message):
    if not message.from_user or not await is_admin(client, message.from_user.id, message.chat.id):
        return
    welcome_data[message.chat.id] = {"enabled": True, "text": DEFAULT_WELCOME, "keyboard": None}
    await message.reply_text("<blockquote>🔄 <b>Welcome message reset to default!</b></blockquote>", parse_mode=ParseMode.HTML)

# ==================== Member Join Event ====================
@Client.on_message(filters.new_chat_members & filters.group)
async def welcome_new_member(client: Client, message: Message):
    chat_id = message.chat.id
    settings = welcome_data.get(chat_id, {"enabled": True, "text": DEFAULT_WELCOME, "keyboard": None})

    if not settings.get("enabled", True):
        return

    bot = await client.get_me()
    for user in message.new_chat_members:
        if user.id == bot.id:
            continue

        raw_template = settings.get("text", DEFAULT_WELCOME)
        keyboard = settings.get("keyboard")

        first_name = user.first_name or "Member"
        mention = f"<a href='tg://user?id={user.id}'>{first_name}</a>"
        chat_title = message.chat.title or "Group"

        # Placeholders replacement
        formatted_text = (
            raw_template
            .replace("{mention}", mention)
            .replace("{name}", first_name)
            .replace("{chat}", chat_title)
            .replace("{id}", str(user.id))
        )

        try:
            await message.reply_text(
                text=formatted_text,
                reply_markup=keyboard,
                parse_mode=ParseMode.HTML,
                disable_web_page_preview=True
            )
        except Exception:
            pass
      
