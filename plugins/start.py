import os
import json
import asyncio
import urllib.request
from pyrogram import Client, filters
from pyrogram.enums import ParseMode
from pyrogram.types import Message, CallbackQuery

BOT_TOKEN = os.environ.get("BOT_TOKEN", "").strip().strip('"').strip("'")

START_TEXT = """<blockquote>👑 <b>Hello {mention}</b>

Main aapka <b>All-in-One Group Manager Bot</b> hoon.
Groups ko manage karne, custom greetings dene,
aur chat environment ko smooth rakhne ke liye tayar hoon!

👑 <b>𝙊𝙒𝙉𝙀𝙍:</b> @Ownerback

Niche diye gaye buttons se explore karein:</blockquote>"""

COMMANDS_MENU_TEXT = """<blockquote>⚡ <b>All Features & Modules:</b>

Aapko jis module ke baare me janna hai,
niche diye gaye button par click karein:</blockquote>"""

ADMIN_TEXT = """<blockquote>🛡️ <b>Admin Commands & Features:</b>

• <code>.promote &lt;title&gt;</code> - Admin banayein (Quick Demote Button)
• <code>.demote</code> - Admin rights revoke karein
• <code>.mute</code> - User ko mute karein (Quick Unmute Button)
• <code>.unmute</code> - User ko unmute karein
• <code>.ban</code> - Permanently ban karein
• <code>.kick</code> - Group se kick karein</blockquote>"""

PIN_TEXT = """<blockquote>📌 <b>Pin & Unpin Management:</b>

• <code>.pin</code> - Reply kiye message ko silently pin karein
• <code>.pin loud</code> - Message pin karein alert notification ke sath
• <code>.unpin</code> - Pinned message par reply karke unpin karein
• <code>.unpinall</code> - Chat ke saare pinned messages clear karein</blockquote>"""

GREETINGS_TEXT = """<blockquote>🎉 <b>Greetings / Welcome System:</b>

• <code>.setwelcome &lt;text&gt;</code> - Custom welcome set karein (Photo, Video & Buttons support).
• <code>.welcome on/off</code> - Greetings toggle karein.
• <code>.getwelcome</code> - Current welcome template check karein.
• <code>.resetwelcome</code> - Default template par reset karein.

<b>Tags:</b> <code>{mention}</code>, <code>{first}</code>, <code>{username}</code>, <code>{chat}</code>, <code>{id}</code></blockquote>"""

QUOTE_TEXT = """<blockquote>🎨 <b>Quotly Sticker Generator:</b>

• <code>.q</code> ya <code>/q</code> - Kisi bhi text message par reply karke stylish Quotly sticker banayein!
• Sender ka profile avatar, name aur message ek round sticker ban jayega.</blockquote>"""

AFK_TEXT = """<blockquote>💤 <b>AFK (Away From Keyboard) System:</b>

• <code>.afk &lt;reason&gt;</code> - AFK status set karein
• Group ke sabhi members ke liye fully functional
• Mention ya reply karne par bot instant notice dega</blockquote>"""

REQUEST_TEXT = """<blockquote>📥 <b>Auto Request Accept System:</b>

• Nayi aane wali join requests ka auto-approval system.
• <code>.requestaccept on</code> - Auto accept chalu karein.
• <code>.requestaccept off</code> - Auto accept band karein.</blockquote>"""

async def call_tg_bot_api(endpoint: str, payload: dict):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/{endpoint}"
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})

    def _sync_post():
        try:
            with urllib.request.urlopen(req, timeout=10) as response:
                return json.loads(response.read().decode("utf-8"))
        except Exception as err:
            print(f"[BotAPI Error] {err}")
            return None

    return await asyncio.to_thread(_sync_post)

# 1. Main Home Menu (Exactly 3 Buttons)
def get_home_keyboard(bot_username: str):
    return {
        "inline_keyboard": [
            [{"text": "⚡ 𝘾𝙊𝙈𝙈𝘼𝙉𝘿𝙎", "callback_data": "menu_commands", "style": "success"}],
            [
                {"text": "👑 𝙊𝙒𝙉𝙀𝙍", "url": "https://t.me/Ownerback", "style": "success"},
                {"text": "✨ 𝘼𝘿𝘿 𝙈𝙀", "url": f"https://t.me/{bot_username}?startgroup=true", "style": "success"}
            ]
        ]
    }

# 2. Commands Sub-Menu
def get_commands_keyboard():
    return {
        "inline_keyboard": [
            [
                {"text": "🛡️ Admin Control", "callback_data": "help_admin", "style": "success"},
                {"text": "📌 Pin System", "callback_data": "help_pin", "style": "success"}
            ],
            [
                {"text": "🎉 Greetings", "callback_data": "help_greetings", "style": "success"},
                {"text": "🎨 Quotes", "callback_data": "help_quote", "style": "success"}
            ],
            [
                {"text": "💤 AFK System", "callback_data": "help_afk", "style": "success"},
                {"text": "📥 Request Accept", "callback_data": "help_request", "style": "success"}
            ],
            [
                {"text": "« Back To Home", "callback_data": "menu_home", "style": "success"}
            ]
        ]
    }

# 3. Detail Back Button
def get_back_to_commands_keyboard():
    return {
        "inline_keyboard": [
            [{"text": "« Back to Commands", "callback_data": "menu_commands", "style": "success"}]
        ]
    }

# ==================== PRIVATE /start ====================
@Client.on_message(filters.command("start", prefixes=[".", "/"]) & filters.private)
async def private_start(client: Client, message: Message):
    try:
        await client.send_reaction(
            chat_id=message.chat.id,
            message_id=message.id,
            emoji="🔥"
        )
    except Exception:
        pass

    bot = await client.get_me()
    mention = f"<a href='tg://user?id={message.from_user.id}'>{message.from_user.first_name}</a>"

    payload = {
        "chat_id": message.chat.id,
        "text": START_TEXT.format(mention=mention),
        "parse_mode": "HTML",
        "reply_markup": get_home_keyboard(bot.username)
    }
    await call_tg_bot_api("sendMessage", payload)

# ==================== GROUP INTRO ====================
@Client.on_message(filters.command("start", prefixes=[".", "/"]) & filters.group)
async def group_start_intro(client: Client, message: Message):
    try:
        await client.send_reaction(
            chat_id=message.chat.id,
            message_id=message.id,
            emoji="🔥"
        )
    except Exception:
        pass

    bot = await client.get_me()
    user_name = message.from_user.first_name if message.from_user else "Member"
    user_mention = f"<a href='tg://user?id={message.from_user.id}'>{user_name}</a>" if message.from_user else "Member"

    group_text = (
        "<blockquote>👋 <b>Hey {user_mention}!</b>\n"
        "✦ ━━━━━━━━━━━━━━━━━━ ✦\n"
        f"Main <b>{bot.first_name}</b> hoon, ek modern group management bot!\n\n"
        "👑 <b>Owner:</b> @Ownerback\n\n"
        "Niche diye gaye buttons se setup karein.</blockquote>"
    ).format(user_mention=user_mention)

    group_markup = {
        "inline_keyboard": [
            [
                {"text": "💬 Help & Features (PM)", "url": f"https://t.me/{bot.username}?start=help", "style": "success"},
                {"text": "✨ Add Me To Group", "url": f"https://t.me/{bot.username}?startgroup=true", "style": "success"}
            ]
        ]
    }

    payload = {
        "chat_id": message.chat.id,
        "text": group_text,
        "parse_mode": "HTML",
        "disable_web_page_preview": True,
        "reply_markup": group_markup
    }
    await call_tg_bot_api("sendMessage", payload)

# ==================== CALLBACK QUERY ROUTER ====================
@Client.on_callback_query()
async def callback_handler(client: Client, query: CallbackQuery):
    data = query.data
    bot = await client.get_me()
    mention = f"<a href='tg://user?id={query.from_user.id}'>{query.from_user.first_name}</a>"

    new_text = ""
    new_markup = None

    if data == "menu_home":
        new_text = START_TEXT.format(mention=mention)
        new_markup = get_home_keyboard(bot.username)
    elif data == "menu_commands":
        new_text = COMMANDS_MENU_TEXT
        new_markup = get_commands_keyboard()
    elif data == "help_admin":
        new_text = ADMIN_TEXT
        new_markup = get_back_to_commands_keyboard()
    elif data == "help_pin":
        new_text = PIN_TEXT
        new_markup = get_back_to_commands_keyboard()
    elif data == "help_greetings":
        new_text = GREETINGS_TEXT
        new_markup = get_back_to_commands_keyboard()
    elif data == "help_quote":
        new_text = QUOTE_TEXT
        new_markup = get_back_to_commands_keyboard()
    elif data == "help_afk":
        new_text = AFK_TEXT
        new_markup = get_back_to_commands_keyboard()
    elif data == "help_request":
        new_text = REQUEST_TEXT
        new_markup = get_back_to_commands_keyboard()

    if new_text and new_markup:
        payload = {
            "chat_id": query.message.chat.id,
            "message_id": query.message.id,
            "text": new_text,
            "parse_mode": "HTML",
            "reply_markup": new_markup
        }
        await call_tg_bot_api("editMessageText", payload)

    try:
        await query.answer()
    except Exception:
        pass
        
