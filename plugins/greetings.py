import os
import re
import random
import time
from pyrogram import Client, filters
from pyrogram.enums import ParseMode, ChatMemberStatus
from pyrogram.types import Message, ChatMemberUpdated, InlineKeyboardMarkup, InlineKeyboardButton

welcome_data = {}
# Deduplication map: {f"{chat_id}_{user_id}": last_welcome_timestamp}
recent_welcomes = {}

DEFAULT_WELCOME = (
    "<blockquote expandable>✨ <b>𝙬𝙚𝙡𝙘𝙤𝙢𝙚 𝙩𝙤 𝙩𝙝𝙚 𝙜𝙧𝙤𝙪𝙥</b> ✨\n"
    "✦ ━━━━━━━━━━━━━━━━━━ ✦\n"
    "👋 Hello {mention}!\n"
    "🎉 Welcome to <b>{chat}</b>!\n"
    "💬 Group rules follow karein aur chill karein!</blockquote>"
)

# Cute & Aesthetic Emoji Palette from Bestie vibes
AESTHETIC_EMOJIS = [
    "🌸", "🎀", "🧸", "🌷", "✨", "🍓", "🍧", "🍒", "💐", "🤍", 
    "🍰", "🩰", "🍬", "🦋", "🫧", "🍯", "🕊️", "🥞", "🍭", "💫"
]

async def is_admin(client: Client, user_id: int, chat_id: int) -> bool:
    try:
        member = await client.get_chat_member(chat_id, user_id)
        return member.status in [ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR]
    except Exception:
        return False

def parse_buttons(raw_text: str):
    if not raw_text:
        return "", []

    btn_regex = re.compile(
        r"\[([^\[\]\(\)\|]+)\](?:\((?:buttonurl:)?\s*(https?://[^\s\)]+)\)|\|\s*(https?://[^\[\]\|\s]+))"
    )

    extracted_buttons = []
    lines = raw_text.split("\n")
    cleaned_lines = []

    for line in lines:
        matches = btn_regex.findall(line)
        if matches:
            row = []
            for m in matches:
                title = m[0].strip()
                url = m[1].strip() if m[1] else m[2].strip()
                clean_title = re.sub(r'^[^\w\s\(\)\[\]\{\}<>\/\\-]+\s*', '', title).strip()
                row.append({"text": clean_title or title, "url": url})
            if row:
                extracted_buttons.append(row)
        else:
            cleaned_lines.append(line)

    cleaned_text = "\n".join(cleaned_lines).rstrip()
    return cleaned_text, extracted_buttons

def build_randomized_keyboard(button_rows):
    if not button_rows:
        return None

    total_buttons = sum(len(r) for r in button_rows)
    chosen_emojis = random.sample(AESTHETIC_EMOJIS, min(total_buttons, len(AESTHETIC_EMOJIS)))
    
    markup_rows = []
    idx = 0
    for row in button_rows:
        new_row = []
        for btn in row:
            emoji = chosen_emojis[idx % len(chosen_emojis)]
            idx += 1
            styled_text = f"{emoji} {btn['text']}"
            new_row.append(InlineKeyboardButton(text=styled_text, url=btn["url"]))
        markup_rows.append(new_row)

    return InlineKeyboardMarkup(markup_rows)

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
    # Smart Anti-Duplicate Lock: Block duplicate welcome for the same user within 15 seconds
    now = time.time()
    dedup_key = f"{chat_id}_{user.id}"
    if dedup_key in recent_welcomes:
        if now - recent_welcomes[dedup_key] < 15:
            return
    recent_welcomes[dedup_key] = now

    settings = welcome_data.get(chat_id, {
        "enabled": True,
        "type": "text",
        "file_id": None,
        "text": DEFAULT_WELCOME,
        "button_rows": []
    })

    if not settings.get("enabled", True):
        return

    raw_template = settings.get("text") or DEFAULT_WELCOME
    button_rows = settings.get("button_rows", [])
    m_type = settings.get("type", "text")
    f_id = settings.get("file_id")

    caption = apply_template_tags(raw_template, user, chat_title)
    markup = build_randomized_keyboard(button_rows)

    try:
        if m_type == "video" and f_id:
            await client.send_video(chat_id=chat_id, video=f_id, caption=caption, parse_mode=ParseMode.HTML, reply_markup=markup)
        elif m_type == "photo" and f_id:
            await client.send_photo(chat_id=chat_id, photo=f_id, caption=caption, parse_mode=ParseMode.HTML, reply_markup=markup)
        elif m_type == "animation" and f_id:
            await client.send_animation(chat_id=chat_id, animation=f_id, caption=caption, parse_mode=ParseMode.HTML, reply_markup=markup)
        else:
            await client.send_message(chat_id=chat_id, text=caption, parse_mode=ParseMode.HTML, disable_web_page_preview=True, reply_markup=markup)
    except Exception as e:
        print(f"[Welcome Error] {e}")

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
            "<blockquote>⚠️ <b>Kisi video/photo par reply karke <code>.setwelcome</code> likhein.</b></blockquote>",
            parse_mode=ParseMode.HTML
        )

    cleaned_text, button_rows = parse_buttons(target_text)
    final_text = format_exact_quotes(cleaned_text)

    welcome_data[chat_id] = {
        "enabled": True,
        "type": media_type,
        "file_id": file_id,
        "text": final_text,
        "button_rows": button_rows
    }

    admin_name = message.from_user.first_name or "Admin"
    btn_count = sum(len(r) for r in button_rows)

    preview = (
        "<blockquote>🎉 <b>𝙬𝙚𝙡𝙘𝙤𝙢𝙚 𝙢𝙚𝙨𝙨𝙖𝙜𝙚 𝙨𝙚𝙩</b> 🎉\n"
        "✦ ━━━━━━━━━━━━━━━━━━ ✦\n"
        f"👮 <b>Set By:</b> <a href='tg://user?id={message.from_user.id}'>{admin_name}</a>\n"
        f"🎬 <b>Media:</b> <code>{media_type.upper()}</code>\n"
        f"🎀 <b>Buttons:</b> <code>{btn_count} Linked (Aesthetic Bestie Pack Active)</code>\n"
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
        welcome_data[chat_id] = {"enabled": True, "type": "text", "file_id": None, "text": DEFAULT_WELCOME, "button_rows": []}

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
    welcome_data[message.chat.id] = {"enabled": True, "type": "text", "file_id": None, "text": DEFAULT_WELCOME, "button_rows": []}
    await message.reply_text("<blockquote>🔄 <b>Welcome message reset to default!</b></blockquote>", parse_mode=ParseMode.HTML)

# ==================== Event 1: Manual Approvals / Invite Link Joins ====================
@Client.on_chat_member_updated()
async def member_status_update(client: Client, update: ChatMemberUpdated):
    old_status = update.old_chat_member.status if update.old_chat_member else None
    new_status = update.new_chat_member.status if update.new_chat_member else None

    # Detects when an admin manually approves a join request OR user joins via invite link
    if old_status in [None, ChatMemberStatus.LEFT, ChatMemberStatus.BANNED] and new_status == ChatMemberStatus.MEMBER:
        bot = await client.get_me()
        user = update.new_chat_member.user
        if not user or user.id == bot.id:
            return
        chat_title = update.chat.title or "Group"
        await send_welcome_payload(client, update.chat.id, user, chat_title)

# ==================== Event 2: Direct / Service Message Joins ====================
@Client.on_message(filters.new_chat_members & filters.group)
async def welcome_new_member_msg(client: Client, message: Message):
    bot = await client.get_me()
    for user in message.new_chat_members:
        if user.id == bot.id:
            continue
        chat_title = message.chat.title or "Group"
        await send_welcome_payload(client, message.chat.id, user, chat_title)
        
