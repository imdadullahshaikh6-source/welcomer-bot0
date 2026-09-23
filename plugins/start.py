import os
import json
import asyncio
import urllib.request
from pyrogram import Client, filters
from pyrogram.types import Message, CallbackQuery

OWNER_USERNAME = "Ownerbackk"
SUPPORT_GROUP_URL = "https://t.me/+UCmLt1cgPhI1MjFl"
START_PHOTO_URL = "https://graph.org/file/d3a2c17942e606f4ec811-9c0373fa8bb10f4448.jpg"

def get_token():
    return os.environ.get("BOT_TOKEN", "").strip().strip('"').strip("'")

# Official Bot API Caller
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

# Exact Stylish Text
DM_START_TEXT = (
    "<blockquote>🌸 <b>𝑯𝒆𝒚 {mention}!! 𝑰'𝒎 𝒁𝒐𝒚𝒂</b> 💖\n"
    "✦ ━━━━━━━━━━━━━━━━━━ ✦\n"
    "<b>𝑴𝒂𝒊𝒏 𝒂𝒂𝒑𝒌𝒆 𝒈𝒓𝒐𝒖𝒑 𝒌𝒊 𝑺𝒎𝒂𝒓𝒕 & 𝑨𝒆𝒔𝒕𝒉𝒆𝒕𝒊𝒄 𝑴𝒂𝒏𝒂𝒈𝒆𝒓 𝒉𝒐𝒐𝒏!</b>\n\n"
    "✨ <i>𝑪𝒖𝒔𝒕𝒐𝒎 𝒂𝒆𝒔𝒕𝒉𝒆𝒕𝒊𝒄 𝒘𝒆𝒍𝒄𝒐𝒎𝒆𝒔</i>\n"
    "🛡️ <i>𝑮𝒓𝒐𝒖𝒑 𝒑𝒓𝒐𝒕𝒆𝒄𝒕𝒊𝒐𝒏 & 𝒔𝒊𝒍𝒆𝒏𝒕 𝒎𝒐𝒅𝒆𝒓𝒂𝒕𝒊𝒐𝒏</i>\n"
    "🎮 <i>𝑴𝒊𝒏𝒊 𝒈𝒂𝒎𝒆𝒔 & 𝑪𝒐𝒖𝒑𝒍𝒆 𝒎𝒂𝒕𝒄𝒉𝒆𝒓</i>\n"
    "💬 <i>𝑨𝑭𝑲 𝒔𝒚𝒔𝒕𝒆𝒎 & 𝒂𝒏𝒕𝒊-𝒔𝒑𝒂𝒎 𝒗𝒊𝒃𝒆𝒔</i>\n\n"
    "<b>𝑵𝒊𝒄𝒉𝒆 𝒅𝒊𝒚𝒆 𝒃𝒖𝒕𝒕𝒐𝒏𝒔 𝒔𝒆 𝒆𝒙𝒑𝒍𝒐𝒓𝒆 𝒌𝒂𝒓𝒆𝒊𝒏:</b></blockquote>"
)

GROUP_START_TEXT = (
    "<blockquote>✨ <b>Zoya is active here!</b> 🎀\n"
    "✦ ━━━━━━━━━━━━━━━━━━ ✦\n"
    "Hey {mention}! Main is group ko safe aur fun rakhne ke liye tayar hoon.\n\n"
    "⚙️ Commands aur settings ke liye mere <b>PM (DM)</b> mein check karein!</blockquote>"
)

HELP_TEXT = (
    "<blockquote>⚡ <b>All Features & Modules:</b>\n"
    "✦ ━━━━━━━━━━━━━━━━━━ ✦\n"
    "Niche diye gaye modules par tap karke controls dekhein:</blockquote>"
)

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
    "<code>[Helpline](https://t.me/link)</code>\n\n"
    "🎨 <b>4. Quotes Format:</b>\n"
    "• Bot automatically captions ko stylish <code>&lt;blockquote&gt;</code> mein wrap kar deta hai.\n\n"
    "🛡️ <b>5. Moderation Format:</b>\n"
    "• Reply karke: <code>.ban</code> | <code>.unban</code> | <code>.mute</code></blockquote>"
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
                {"text": "🎮 Games & Fun", "callback_data": "cmd_fun", "style": "success"}
            ],
            [
                {"text": "✨ Extra", "callback_data": "cmd_extra", "style": "success"},
                {"text": "📖 Formatting Guide", "callback_data": "open_formatting", "style": "success"}
            ],
            [
                {"text": "« Back To Home", "callback_data": "back_to_start", "style": "success"}
            ]
        ]
    }

@Client.on_message(filters.command("start", prefixes=["/", "."]))
async def start_handler(client: Client, message: Message):
    # User ke /start par Flame blast reaction
    asyncio.create_task(
        call_tg_bot_api("setMessageReaction", {
            "chat_id": message.chat.id,
            "message_id": message.id,
            "reaction": [{"type": "emoji", "emoji": "🔥"}],
            "is_big": True
        })
    )

    bot = await client.get_me()
    first_name = message.from_user.first_name or "Friend"
    mention = f"<a href='tg://user?id={message.from_user.id}'>{first_name}</a>"

    if len(message.command) > 1 and message.command[1].lower() == "help":
        payload = {
            "chat_id": message.chat.id,
            "text": HELP_TEXT,
            "parse_mode": "HTML",
            "reply_markup": get_commands_menu()
        }
        resp = await call_tg_bot_api("sendMessage", payload)
        if resp and resp.get("ok"):
            await asyncio.sleep(0.3)
            await call_tg_bot_api("setMessageReaction", {
                "chat_id": message.chat.id,
                "message_id": resp["result"]["message_id"],
                "reaction": [{"type": "emoji", "emoji": "🔥"}],
                "is_big": True
            })
        return

    if message.chat.type.name == "PRIVATE":
        # 1. Pehle banner photo bhejo (Aero style)
        photo_resp = await call_tg_bot_api("sendPhoto", {
            "chat_id": message.chat.id,
            "photo": START_PHOTO_URL
        })

        # 2. Phir text message bhejo jiske upar reaction exact corner me aayega
        caption = DM_START_TEXT.format(mention=mention)
        markup = get_start_markup(bot.username)
        
        text_payload = {
            "chat_id": message.chat.id,
            "text": caption,
            "parse_mode": "HTML",
            "disable_web_page_preview": True,
            "reply_markup": markup
        }
        resp = await call_tg_bot_api("sendMessage", text_payload)

        # Text message par exact corner reaction aur blast
        if resp and resp.get("ok"):
            bot_msg_id = resp["result"]["message_id"]
            await asyncio.sleep(0.4)
            await call_tg_bot_api("setMessageReaction", {
                "chat_id": message.chat.id,
                "message_id": bot_msg_id,
                "reaction": [{"type": "emoji", "emoji": "🔥"}],
                "is_big": True
            })
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

@Client.on_message(filters.command("help", prefixes=["/", "."]))
async def help_handler(client: Client, message: Message):
    bot = await client.get_me()
    first_name = message.from_user.first_name or "Friend"
    mention = f"<a href='tg://user?id={message.from_user.id}'>{first_name}</a>"

    if message.chat.type.name == "PRIVATE":
        payload = {
            "chat_id": message.chat.id,
            "text": HELP_TEXT,
            "parse_mode": "HTML",
            "reply_markup": get_commands_menu()
        }
        resp = await call_tg_bot_api("sendMessage", payload)
        if resp and resp.get("ok"):
            await asyncio.sleep(0.3)
            await call_tg_bot_api("setMessageReaction", {
                "chat_id": message.chat.id,
                "message_id": resp["result"]["message_id"],
                "reaction": [{"type": "emoji", "emoji": "🔥"}],
                "is_big": True
            })
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
    await call_tg_bot_api("editMessageText", {
        "chat_id": query.message.chat.id,
        "message_id": query.message.id,
        "text": HELP_TEXT,
        "parse_mode": "HTML",
        "reply_markup": get_commands_menu()
    })
    await query.answer()

@Client.on_callback_query(filters.regex("^open_formatting$"))
async def formatting_callback(client: Client, query: CallbackQuery):
    back_btn = {
        "inline_keyboard": [
            [{"text": "« Back To Modules", "callback_data": "open_commands", "style": "success"}]
        ]
    }
    await call_tg_bot_api("editMessageText", {
        "chat_id": query.message.chat.id,
        "message_id": query.message.id,
        "text": FORMATTING_GUIDE_TEXT,
        "parse_mode": "HTML",
        "reply_markup": back_btn
    })
    await query.answer()

@Client.on_callback_query(filters.regex("^back_to_start$"))
async def back_start_callback(client: Client, query: CallbackQuery):
    bot = await client.get_me()
    first_name = query.from_user.first_name or "Friend"
    mention = f"<a href='tg://user?id={query.from_user.id}'>{first_name}</a>"
    caption = DM_START_TEXT.format(mention=mention)
    
    await call_tg_bot_api("editMessageText", {
        "chat_id": query.message.chat.id,
        "message_id": query.message.id,
        "text": caption,
        "parse_mode": "HTML",
        "reply_markup": get_start_markup(bot.username)
    })
    await query.answer()

@Client.on_callback_query(filters.regex(r"^cmd_(admin|pin|greet|extra|fun)$"))
async def sub_commands_view(client: Client, query: CallbackQuery):
    mod = query.data.split("_")[1]
    
    details = {
        "admin": (
            "🛡️ <b>Admin Controls:</b>\n"
            "✦ ━━━━━━━━━━━━━━━━━━ ✦\n"
            "• <code>.ban</code> - User ko ban karein\n"
            "• <code>.unban</code> - User ko unban karein\n"
            "• <code>.kick</code> - User ko group se nikalen\n"
            "• <code>.mute</code> / <code>.unmute</code> - Member mute/unmute\n"
            "• <code>.promote &lt;title&gt;</code> - Admin banayein title ke sath\n"
            "• <code>.demote</code> - Admin rights hatayein"
        ),
        "pin": (
            "📌 <b>Pin Controls:</b>\n"
            "✦ ━━━━━━━━━━━━━━━━━━ ✦\n"
            "• <code>.pin</code> - Silent pin\n"
            "• <code>.pin loud</code> - Message pin + notification\n"
            "• <code>.unpin</code> - Message unpin\n"
            "• <code>.unpinall</code> - Saare unpin karein"
        ),
        "greet": (
            "🎉 <b>Greetings:</b>\n"
            "✦ ━━━━━━━━━━━━━━━━━━ ✦\n"
            "• <code>.setwelcome</code> - Media/Text caption par reply karein\n"
            "• <code>.welcome on/off</code> - Greetings on/off\n"
            "• <code>.getwelcome</code> - Preview current welcome\n"
            "• <code>.resetwelcome</code> - Reset to default"
        ),
        "fun": (
            "🎮 <b>Games & Fun Center:</b>\n"
            "✦ ━━━━━━━━━━━━━━━━━━ ✦\n"
            "• <code>.couple</code> ya <code>.ship</code> - Group me daily couple match photo card ke sath! 💖\n"
            "• <code>.dice</code> - Animated dice rolling challenge 🎲\n"
            "• <code>.dart</code> - Dart board shoot 🎯\n"
            "• <code>.basket</code> - Basketball shoot 🏀\n"
            "• <code>.football</code> - Football penalty kick ⚽\n"
            "• <code>.slot</code> - Casino 777 jackpot spin 🎰"
        ),
        "extra": (
            "✨ <b>Extra & Stickers:</b>\n"
            "✦ ━━━━━━━━━━━━━━━━━━ ✦\n"
            "💤 <b>AFK System:</b>\n"
            "• <code>.afk &lt;reason&gt;</code> - Offline status lagayein.\n"
            "• Return aane par automated <i>Welcome Back</i> notice aayega.\n\n"
            "🎨 <b>Stickers & Quotes:</b>\n"
            "• <code>.q</code> - Normal sticker quote banayein.\n"
            "• <code>.qr</code> - Replied message preview ke sath quote sticker banayein.\n"
            "• <code>.kang [emoji]</code> - Kisi bhi image/sticker par reply karke apna sticker pack banayein."
        )
    }
    
    text = f"<blockquote>{details.get(mod, 'Module details')}</blockquote>"
    back_btn = {
        "inline_keyboard": [
            [{"text": "« Back To Modules", "callback_data": "open_commands", "style": "success"}]
        ]
    }
    
    await call_tg_bot_api("editMessageText", {
        "chat_id": query.message.chat.id,
        "message_id": query.message.id,
        "text": text,
        "parse_mode": "HTML",
        "reply_markup": back_btn
    })
    await query.answer()
    
