from pyrogram import Client, filters
from pyrogram.enums import ParseMode
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, Message

def colored_button(text: str, callback_data: str = None, url: str = None, style: str = "primary"):
    kwargs = {"text": text}
    if callback_data:
        kwargs["callback_data"] = callback_data
    if url:
        kwargs["url"] = url
    try:
        return InlineKeyboardButton(**kwargs, style=style)
    except TypeError:
        return InlineKeyboardButton(**kwargs)

START_TEXT = """<blockquote>👑 <b>Hello {mention}</b>

Main aapka <b>All-in-One Group Manager Bot</b> hoon.
Groups ko manage karne, custom greetings dene,
aur chat environment ko smooth rakhne ke liye tayar hoon!

Niche diye gaye colored buttons se features explore karein:</blockquote>"""

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

def start_keyboard(bot_username: str):
    return InlineKeyboardMarkup([
        [
            colored_button("🔴 Admin Features", callback_data="help_admin", style="danger"),
            colored_button("🔵 Pin System", callback_data="help_pin", style="primary")
        ],
        [
            colored_button("🟢 Greetings", callback_data="help_greetings", style="success"),
            colored_button("🔵 Quote Sticker", callback_data="help_quote", style="primary")
        ],
        [
            colored_button("🔵 AFK System", callback_data="help_afk", style="primary"),
            colored_button("🟢 Request Accept", callback_data="help_request", style="success")
        ],
        [
            colored_button("🔵 Add Me To Your Group", url=f"https://t.me/{bot_username}?startgroup=true", style="primary")
        ]
    ])

BACK_KEYBOARD = InlineKeyboardMarkup([
    [colored_button("« Back", callback_data="help_back", style="primary")]
])

# ==================== PRIVATE /start ====================
@Client.on_message(filters.command("start", prefixes=[".", "/"]) & filters.private)
async def private_start(client: Client, message: Message):
    bot = await client.get_me()
    mention = f"<a href='tg://user?id={message.from_user.id}'>{message.from_user.first_name}</a>"
    await message.reply_text(
        text=START_TEXT.format(mention=mention),
        reply_markup=start_keyboard(bot.username),
        parse_mode=ParseMode.HTML
    )

# ==================== GROUP INTRO ====================
@Client.on_message(filters.command("start", prefixes=[".", "/"]) & filters.group)
async def group_start_intro(client: Client, message: Message):
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
        "Features dekhne ke liye niche DM button dabayein.</blockquote>"
    ).format(user_mention=user_mention)

    group_keyboard = InlineKeyboardMarkup([
        [
            colored_button("🔵 Help & Features (PM)", url=f"https://t.me/{bot.username}?start=help", style="primary"),
            colored_button("🟢 Add Me", url=f"https://t.me/{bot.username}?startgroup=true", style="success")
        ]
    ])

    await message.reply_text(
        text=group_text,
        reply_markup=group_keyboard,
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True
    )

# ==================== INLINE CALLBACKS ====================
@Client.on_callback_query()
async def callback_handler(client: Client, query: CallbackQuery):
    data = query.data
    bot = await client.get_me()
    mention = f"<a href='tg://user?id={query.from_user.id}'>{query.from_user.first_name}</a>"

    if data == "help_admin":
        await query.message.edit_text(text=ADMIN_TEXT, reply_markup=BACK_KEYBOARD, parse_mode=ParseMode.HTML)
    elif data == "help_pin":
        await query.message.edit_text(text=PIN_TEXT, reply_markup=BACK_KEYBOARD, parse_mode=ParseMode.HTML)
    elif data == "help_greetings":
        await query.message.edit_text(text=GREETINGS_TEXT, reply_markup=BACK_KEYBOARD, parse_mode=ParseMode.HTML)
    elif data == "help_quote":
        await query.message.edit_text(text=QUOTE_TEXT, reply_markup=BACK_KEYBOARD, parse_mode=ParseMode.HTML)
    elif data == "help_afk":
        await query.message.edit_text(text=AFK_TEXT, reply_markup=BACK_KEYBOARD, parse_mode=ParseMode.HTML)
    elif data == "help_request":
        await query.message.edit_text(text=REQUEST_TEXT, reply_markup=BACK_KEYBOARD, parse_mode=ParseMode.HTML)
    elif data == "help_back":
        await query.message.edit_text(
            text=START_TEXT.format(mention=mention),
            reply_markup=start_keyboard(bot.username),
            parse_mode=ParseMode.HTML
        )
    await query.answer()
    
