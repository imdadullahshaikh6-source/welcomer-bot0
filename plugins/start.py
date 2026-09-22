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

# Pure Telegram Bot API HTTP Caller jo Button Colors (style) ko support karta hai
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
        except urllib.error.HTTPError as he:
            err = he.read().decode("utf-8", errors="ignore")
            print(f"[BotAPI HTTP {he.code}] {err}")
            return None
        except Exception as e:
            print(f"[BotAPI Error] {e}")
            return None

    return await asyncio.to_thread(_sync)

START_TEXT = (
    "<blockquote>👑 <b>Hello {mention}!!</b>\n\n"
    "Main aapka <b>All-in-One Group Manager Bot</b> hoon.\n"
    "Groups ko manage karne, custom greetings dene,\n"
    "aur chat environment ko smooth rakhne ke liye tayar hoon!\n\n"
    f"👑 <b>OWNER:</b> @{OWNER_USERNAME}\n\n"
    "Niche diye gaye buttons se explore karein:</blockquote>"
)

HELP_TEXT = (
    "<blockquote>⚡ <b>All Features & Modules:</b>\n"
    "✦ ━━━━━━━━━━━━━━━━━━ ✦\n"
    "Niche diye gaye modules par tap karke controls dekhein:</blockquote>"
)

def get_start_markup(bot_username: str):
    owner_url = f"https://t.me/{OWNER_USERNAME}"
    add_bot_url = f"https://t.me/{bot_username}?startgroup=true"
    
    return {
        "inline_keyboard": [
            [
                {"text": "⚡ COMMANDS", "callback_data": "open_commands", "style": "success"}
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

@Client.on_message(filters.command("start") & filters.private)
async def start_handler(client: Client, message: Message):
    bot = await client.get_me()
    first_name = message.from_user.first_name or "User"
    mention = f"<a href='tg://user?id={message.from_user.id}'>{first_name}</a>"
    
    caption = START_TEXT.format(mention=mention)
    markup = get_start_markup(bot.username)
    
    payload = {
        "chat_id": message.chat.id,
        "text": caption,
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

@Client.on_callback_query(filters.regex("^back_to_start$"))
async def back_start_callback(client: Client, query: CallbackQuery):
    bot = await client.get_me()
    first_name = query.from_user.first_name or "User"
    mention = f"<a href='tg://user?id={query.from_user.id}'>{first_name}</a>"
    caption = START_TEXT.format(mention=mention)
    
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
    
