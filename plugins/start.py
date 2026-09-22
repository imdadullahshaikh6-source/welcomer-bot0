import os
import json
import asyncio
import urllib.request
from pyrogram import Client, filters
from pyrogram.types import Message, CallbackQuery

OWNER_USERNAME = "Ownerbackk"
SUPPORT_GROUP_URL = "https://t.me/+UCmLt1cgPhI1MjFl"

def get_token():
    return os.environ.get("BOT_TOKEN", "").strip().strip('"').strip("'")

# Bot API HTTP Caller for styles and reactions
async def call_tg_bot_api(endpoint: str, payload: dict):
    token = get_token()
    if not token:
        return None

    url = f"https://api.telegram.org/bot{token}/{endpoint}"
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})

    def _sync():
        try:
            with urllib.request.urlopen(req, timeout=12) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except Exception:
            return None

    return await asyncio.to_thread(_sync)

# Aesthetic Zoya Intro for Private DM
DM_START_TEXT = (
    "<blockquote>🌸 <b>Hey {mention}!! I'm Zoya</b> 💖\n"
    "✦ ━━━━━━━━━━━━━━━━━━ ✦\n"
    "Main aapke group ki <b>Smart & Aesthetic Manager</b> hoon!\n\n"
    "✨ <i>Custom aesthetic welcomes</i>\n"
    "🛡️ <i>Group protection & silent moderation</i>\n"
    "💬 <i>Auto approvals & anti-spam vibes</i>\n\n"
    f"👑 <b>Owner:</b> @{OWNER_USERNAME}\n\n"
    "Niche diye buttons se explore karein:</blockquote>"
)

# Cute Zoya Intro when /start is used in Groups
GROUP_START_TEXT = (
    "<blockquote>✨ <b>Zoya is active here!</b> 🎀\n"
    "✦ ━━━━━━━━━━━━━━━━━━ ✦\n"
    "Hey {mention}! Main is group ko safe aur clean rakhne ke liye tayar hoon.\n\n"
    "⚙️ Commands aur formatting guide ke liye mere <b>PM (DM)</b> mein check karein!</blockquote>"
)

HELP_TEXT = (
    "<blockquote>⚡ <b>All Features & Modules:</b>\n"
    "✦ ━━━━━━━━━━━━━━━━━━ ✦\n"
    "Niche diye gaye modules par tap karke controls dekhein:</blockquote>"
)

# Complete Formatted Guide for Welcome, Buttons, Tags and Quotes
FORMATTING_GUIDE_TEXT = (
    "<blockquote>📖 <b>𝙁𝙤𝙧𝙢𝙖𝙩𝙩𝙞𝙣𝙜 & 𝙎𝙮𝙣𝙩𝙖𝙭 𝙂𝙪𝙞𝙙𝙚</b> ✨\n"
    "✦ ━━━━━━━━━━━━━━━━━━ ✦\n\n"
    "🎀 <b>1. Welcome Message Set Karna:</b>\n"
    "Kisi bhi Video/Photo ke caption mein apna text likhein aur us par reply karke <code>.setwelcome</code> likhein.\n\n"
    "🏷️ <b>2. Auto Tags (Dynamic Placeholders):</b>\n"
    "• <code>{mention}</code> - User ka clickable name\n"
    "• <code>{id}</code> - User ki numeric Telegram ID\n"
    "• <code>{username}</code> - User ka @username\n"
    "• <code>{chat}</code> - Group ka title/naam\n\n"
    "🔘 <b>3. Buttons Lagane Ka Tarika:</b>\n"
    "Message caption ke aakhri lines mein is tarah likhein:\n"
    "• <i>Single Button:</i>\n"
    "<code>[Button Title](https://t.me/link)</code>\n"
    "• <i>Alag-Alag Rows (Line change karein):</i>\n"
    "<code>[Music](https://t.me/link)</code>\n"
    "<code>[Helpline](https://t.me/link)</code>\n"
    "• <i>Ek Hi Line Mein Do Buttons:</i>\n"
    "<code>[Channel](https://t.me/link) [Group](https://t.me/link)</code>\n\n"
    "🎨 <b>4. Quotes Format (Expandable):</b>\n"
    "• Bot automatically aapke captions ko stylish <code>&lt;blockquote expandable&gt;</code> mein wrap kar deta hai jisse message clean aur collapseable dikhta hai.\n\n"
    "🛡️ <b>5. Moderation Format:</b>\n"
    "• Reply karke: <code>.ban</code> | <code>.unban</code> | <code>.mute</code>\n"
    "• Direct Tag karke: <code>.ban @username</code> ya <code>.ban Noor</code></blockquote>"
)

def get_start_markup(bot_username: str):
    owner_url = f"https://t.me/{OWNER_USERNAME}"
    add_bot_url = f"https://t.me/{bot_username}?startgroup=true"
    
    return {
        "inline_keyboard": [
            [
                {"text": "⚡ COMMANDS", "callback_data": "open_commands", "style": "success"},
                {"text": "🎨 FORMATTING", "callback_data": "open_formatting", "style": "success"}
            ],
            [
                {"text": "👑 OWNER", "url": owner_url, "style": "success"},
                {"text": "✨ ADD ME", "url": add_bot_url, "style": "success"}
            ],
            [
                {"text": "💬 SUPPORT", "url": SUPPORT_GROUP_URL, "style": "success"}
            ]
        ]
    }

def get_group_markup(bot_username: str):
    return {
        "inline_keyboard": [
            [
                {"text": "💌 Start Zoya in PM", "url": f"https://t.me/{bot_username}?start=help", "style": "success"}
            ],
            [
                {"text": "💬 Support", "url": SUPPORT_GROUP_URL, "style": "success"}
            ]
        ]
    }

def get_commands_menu():
    return {
        "inline_keyboard": [
            [
                {"text": "🛡️ Admin Control", "callback_data": "cmd_admin", "style": "success"},
                {"text": "📌 Pin System", "callback_data": "cmd_pin", "style": "success"}
            ],
            [
                {"text": "🎉 Greetings", "callback_data": "cmd_greet", "style": "success"},
                {"text": "🎨 Quotes", "callback_data": "cmd_quotes", "style": "success"}
            ],
            [
                {"text": "💤 AFK System", "callback_data": "cmd_afk", "style": "success"},
                {"text": "📩 Request Accept", "callback_data": "cmd_req", "style": "success"}
            ],
            [
                {"text": "« Back To Home", "callback_data": "back_to_start", "style": "success"}
            ]
        ]
    }

# Handles /start in BOTH Private and Groups
@Client.on_message(filters.command("start", prefixes=["/", "."]))
async def start_handler(client: Client, message: Message):
    # Reaction handling
    try:
        reaction_payload = {
            "chat_id": message.chat.id,
            "message_id": message.id,
            "reaction": [{"type": "emoji", "emoji": "🔥"}]
        }
        await call_tg_bot_api("setMessageReaction", reaction_payload)
    except Exception:
        pass

    bot = await client.get_me()
    first_name = message.from_user.first_name or "Friend"
    mention = f"<a href='tg://user?id={message.from_user.id}'>{first_name}</a>"

    # Private DM Flow
    if message.chat.type.name == "PRIVATE":
        caption = DM_START_TEXT.format(mention=mention)
        markup = get_start_markup(bot.username)
        
        payload = {
            "chat_id": message.chat.id,
            "text": caption,
            "parse_mode": "HTML",
            "disable_web_page_preview": True,
            "reply_markup": markup
        }
        await call_tg_bot_api("sendMessage", payload)

    # Group Flow
    else:
        caption = GROUP_START_TEXT.format(mention=mention)
        markup = get_group_markup(bot.username)

        payload = {
            "chat_id": message.chat.id,
            "text": caption,
            "reply_to_message_id": message.id,
            "parse_mode": "HTML",
            "disable_web_page_preview": True,
            "reply_markup": markup
        }
        await call_tg_bot_api("sendMessage", payload)

@Client.on_callback_query(filters.regex("^open_commands$"))
async def commands_callback(client: Client, query: CallbackQuery):
    payload = {
        "chat_id": query.message.chat.id,
        "message_id": query.message.id,
        "text": HELP_TEXT,
        "parse_mode": "HTML",
        "reply_markup": get_commands_menu()
    }
    await call_tg_bot_api("editMessageText", payload)
    await query.answer()

@Client.on_callback_query(filters.regex("^open_formatting$"))
async def formatting_callback(client: Client, query: CallbackQuery):
    back_btn = {
        "inline_keyboard": [
            [{"text": "« Back To Home", "callback_data": "back_to_start", "style": "success"}]
        ]
    }
    payload = {
        "chat_id": query.message.chat.id,
        "message_id": query.message.id,
        "text": FORMATTING_GUIDE_TEXT,
        "parse_mode": "HTML",
        "disable_web_page_preview": True,
        "reply_markup": back_btn
    }
    await call_tg_bot_api("editMessageText", payload)
    await query.answer()

@Client.on_callback_query(filters.regex("^back_to_start$"))
async def back_start_callback(client: Client, query: CallbackQuery):
    bot = await client.get_me()
    first_name = query.from_user.first_name or "Friend"
    mention = f"<a href='tg://user?id={query.from_user.id}'>{first_name}</a>"
    caption = DM_START_TEXT.format(mention=mention)
    
    payload = {
        "chat_id": query.message.chat.id,
        "message_id": query.message.id,
        "text": caption,
        "parse_mode": "HTML",
        "disable_web_page_preview": True,
        "reply_markup": get_start_markup(bot.username)
    }
    await call_tg_bot_api("editMessageText", payload)
    await query.answer()

@Client.on_callback_query(filters.regex(r"^cmd_(admin|pin|greet|quotes|afk|req)$"))
async def sub_commands_view(client: Client, query: CallbackQuery):
    mod = query.data.split("_")[1]
    
    details = {
        "admin": "🛡️ <b>Admin Controls:</b>\n• <code>.promote &lt;title&gt;</code>\n• <code>.demote</code>\n• <code>.mute</code> / <code>.unmute</code>\n• <code>.ban</code> / <code>.kick</code>",
        "pin": "📌 <b>Pin Controls:</b>\n• <code>.pin</code> (silent)\n• <code>.pin loud</code>\n• <code>.unpin</code> / <code>.unpinall</code>",
        "greet": "🎉 <b>Greetings:</b>\n• <code>.setwelcome</code> (Media caption reply)\n• <code>.welcome on/off</code>\n• <code>.getwelcome</code>\n• <code>.resetwelcome</code>",
        "quotes": "🎨 <b>Quotes Engine:</b>\n• Expandable aesthetic blockquote format activated automatically!",
        "afk": "💤 <b>AFK Module:</b>\n• <code>.afk &lt;reason&gt;</code> to set offline status.",
        "req": "📩 <b>Join Requests:</b>\n• Auto-approves group join requests instantly."
    }
    
    text = f"<blockquote>{details.get(mod, 'Module details')}</blockquote>"
    back_btn = {
        "inline_keyboard": [
            [{"text": "« Back To Modules", "callback_data": "open_commands", "style": "success"}]
        ]
    }
    
    payload = {
        "chat_id": query.message.chat.id,
        "message_id": query.message.id,
        "text": text,
        "parse_mode": "HTML",
        "reply_markup": back_btn
    }
    await call_tg_bot_api("editMessageText", payload)
    await query.answer()
    
