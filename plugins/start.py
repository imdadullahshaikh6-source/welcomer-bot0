from pyrogram import Client, filters
from pyrogram.enums import ParseMode
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

START_TEXT = """<blockquote>👑 <b>Hello {mention}</b>

Main aapka <b>All-in-One Group Manager Bot</b> hoon.
Groups ko manage karne, join requests auto-accept karne,
aur text ko stickers me badalne ke liye tayar hoon!

Niche diye gaye menu se mere features check karein:</blockquote>"""

ADMIN_TEXT = """<blockquote>🛡️ <b>Admin Commands & Features:</b>

• <code>.promote &lt;title&gt;</code> - Admin banayein (Quick Demote Button)
• <code>.demote</code> - Admin rights revoke karein
• <code>.mute</code> - User ko mute karein (Quick Unmute Button)
• <code>.unmute</code> - User ko unmute karein
• <code>.ban</code> - Permanently ban karein
• <code>.kick</code> - Group se kick karein</blockquote>"""

AFK_TEXT = """<blockquote>💤 <b>AFK (Away From Keyboard) System:</b>

• <code>.afk &lt;reason&gt;</code> - AFK status set karein
• Group ke sabhi members ke liye fully functional
• Mention ya reply karne par bot instant notice dega
• Wapas aane par automatically disable ho jayega</blockquote>"""

WELCOMER_TEXT = """<blockquote>✨ <b>Join Welcomer & Automation:</b>

• Pending join requests auto-approval system
• New users ke aane par custom quote welcome message
• <code>.start</code> - Welcomer automation on karein
• <code>.stop</code> - Welcomer automation pause karein</blockquote>"""

QUOTE_TEXT = """<blockquote>🎨 <b>Quotly Sticker Generator:</b>

• <code>.q</code> ya <code>/q</code> - Kisi bhi text message par reply karke stylish Quotly sticker banayein!
• Sender ka profile photo, name aur text ek round aesthetic sticker ban jayega.
• Group ka koi bhi member is feature ka use kar sakta hai.</blockquote>"""

def start_keyboard(bot_username: str):
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🛡️ Admin Features", callback_data="help_admin"),
            InlineKeyboardButton("💤 AFK System", callback_data="help_afk")
        ],
        [
            InlineKeyboardButton("✨ Join Welcomer", callback_data="help_welcomer"),
            InlineKeyboardButton("🎨 Quote Sticker", callback_data="help_quote")
        ],
        [
            InlineKeyboardButton("➕ Add Me To Your Group", url=f"https://t.me/{bot_username}?startgroup=true")
        ]
    ])

BACK_KEYBOARD = InlineKeyboardMarkup([
    [InlineKeyboardButton("« Back", callback_data="help_back")]
])

@Client.on_message(filters.command("start") & filters.private)
async def private_start(client, message):
    bot = await client.get_me()
    mention = f"<a href='tg://user?id={message.from_user.id}'>{message.from_user.first_name}</a>"
    await message.reply_text(
        text=START_TEXT.format(mention=mention),
        reply_markup=start_keyboard(bot.username),
        parse_mode=ParseMode.HTML
    )

@Client.on_callback_query()
async def callback_handler(client, query: CallbackQuery):
    data = query.data
    bot = await client.get_me()
    mention = f"<a href='tg://user?id={query.from_user.id}'>{query.from_user.first_name}</a>"

    if data == "help_admin":
        await query.message.edit_text(text=ADMIN_TEXT, reply_markup=BACK_KEYBOARD, parse_mode=ParseMode.HTML)
    elif data == "help_afk":
        await query.message.edit_text(text=AFK_TEXT, reply_markup=BACK_KEYBOARD, parse_mode=ParseMode.HTML)
    elif data == "help_welcomer":
        await query.message.edit_text(text=WELCOMER_TEXT, reply_markup=BACK_KEYBOARD, parse_mode=ParseMode.HTML)
    elif data == "help_quote":
        await query.message.edit_text(text=QUOTE_TEXT, reply_markup=BACK_KEYBOARD, parse_mode=ParseMode.HTML)
    elif data == "help_back":
        await query.message.edit_text(
            text=START_TEXT.format(mention=mention),
            reply_markup=start_keyboard(bot.username),
            parse_mode=ParseMode.HTML
        )
    await query.answer()
    
