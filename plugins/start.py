import asyncio
from pyrogram import Client, filters
from pyrogram.enums import ParseMode
from pyrogram.types import Message, CallbackQuery

START_TEXT = """<blockquote>👑 <b>Hello {mention}</b>

Main aapka <b>All-in-One Group Manager Bot</b> hoon.
Groups ko manage karne, custom greetings dene,
aur chat environment ko smooth rakhne ke liye tayar hoon!

Niche diye gaye buttons par click karke features explore karein:</blockquote>"""

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

def get_start_markup(bot_username: str):
    return {
        "inline_keyboard": [
            [{"text": "⚡ Commands", "callback_data": "help_admin", "style": "success"}],
            [
                {"text": "📌 Pin System", "callback_data": "help_pin", "style": "success"},
                {"text": "🎉 Greetings", "callback_data": "help_greetings", "style": "success"}
            ],
            [
                {"text": "🎨 Quotes", "callback_data": "help_quote", "style": "success"},
                {"text": "💤 AFK System", "callback_data": "help_afk", "style": "success"}
            ],
            [{"text": "📥 Request Accept", "callback_data": "help_request", "style": "success"}],
            [{"text": "✨ Add Me", "url": f"https://t.me/{bot_username}?startgroup=true", "style": "success"}]
        ]
    }

BACK_MARKUP = {
    "inline_keyboard": [
        [{"text": "« Back", "callback_data": "help_back", "style": "success"}]
    ]
}

# ==================== PRIVATE /start (With Flame Reaction) ====================
@Client.on_message(filters.command("start", prefixes=[".", "/"]) & filters.private)
async def private_start(client: Client, message: Message):
    # Send Flame / Fire reaction to user's /start message
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

    try:
        await client.send_message(
            chat_id=message.chat.id,
            text=START_TEXT.format(mention=mention),
            reply_markup=get_start_markup(bot.username),
            parse_mode=ParseMode.HTML
        )
    except Exception:
        from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
        fallback_kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("⚡ Commands", callback_data="help_admin")],
            [InlineKeyboardButton("📌 Pin", callback_data="help_pin"), InlineKeyboardButton("🎉 Greetings", callback_data="help_greetings")],
            [InlineKeyboardButton("🎨 Quotes", callback_data="help_quote"), InlineKeyboardButton("💤 AFK", callback_data="help_afk")],
            [InlineKeyboardButton("📥 Request Accept", callback_data="help_request")],
            [InlineKeyboardButton("✨ Add Me", url=f"https://t.me/{bot.username}?startgroup=true")]
        ])
        await message.reply_text(
            text=START_TEXT.format(mention=mention),
            reply_markup=fallback_kb,
            parse_mode=ParseMode.HTML
        )

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
        "⚡ <b>Quick Features:</b>\n"
        "• 🛡️ <i>Admin Control (.promote, .demote, .mute, .ban)</i>\n"
        "• 📌 <i>Pin Management (.pin, .unpin)</i>\n"
        "• 🎉 <i>Custom Greetings (.setwelcome)</i>\n"
        "• 🎨 <i>Quote Stickers (.q)</i>\n"
        "• 💤 <i>AFK System (.afk)</i>\n"
        "• 📥 <i>Auto Request Accept (.requestaccept)</i>\n\n"
        "Features dekhne ke liye niche button dabayein.</blockquote>"
    ).format(user_mention=user_mention)

    group_markup = {
        "inline_keyboard": [
            [{"text": "💬 Help & Features (PM)", "url": f"https://t.me/{bot.username}?start=help", "style": "success"}],
            [{"text": "✨ Add Me To Group", "url": f"https://t.me/{bot.username}?startgroup=true", "style": "success"}]
        ]
    }

    try:
        await client.send_message(
            chat_id=message.chat.id,
            text=group_text,
            reply_markup=group_markup,
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=True
        )
    except Exception:
        from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
        fallback_kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("💬 Help & Features (PM)", url=f"https://t.me/{bot.username}?start=help")],
            [InlineKeyboardButton("✨ Add Me To Group", url=f"https://t.me/{bot.username}?startgroup=true")]
        ])
        await message.reply_text(
            text=group_text,
            reply_markup=fallback_kb,
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=True
        )

# ==================== CALLBACKS ====================
@Client.on_callback_query()
async def callback_handler(client: Client, query: CallbackQuery):
    data = query.data
    bot = await client.get_me()
    mention = f"<a href='tg://user?id={query.from_user.id}'>{query.from_user.first_name}</a>"

    text = ""
    markup = BACK_MARKUP

    if data == "help_admin":
        text = ADMIN_TEXT
    elif data == "help_pin":
        text = PIN_TEXT
    elif data == "help_greetings":
        text = GREETINGS_TEXT
    elif data == "help_quote":
        text = QUOTE_TEXT
    elif data == "help_afk":
        text = AFK_TEXT
    elif data == "help_request":
        text = REQUEST_TEXT
    elif data == "help_back":
        text = START_TEXT.format(mention=mention)
        markup = get_start_markup(bot.username)

    try:
        await client.edit_message_text(
            chat_id=query.message.chat.id,
            message_id=query.message.id,
            text=text,
            reply_markup=markup,
            parse_mode=ParseMode.HTML
        )
    except Exception:
        pass
    await query.answer()
    
