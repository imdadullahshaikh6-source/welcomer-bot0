from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

START_TEXT = """
> 👑 **Hello {mention}**
> 
> Main aapka **All-in-One Group Manager Bot** hoon. 
> Groups ko manage karne, join requests auto-accept karne, 
> aur pure chat environment ko maintain karne ke liye tayar hoon!
> 
> Niche diye gaye menu se mere features check karein:
"""

ADMIN_TEXT = """
> 🛡️ **Admin Commands & Features:**
> 
> • `.promote <title>` - Admin banayein (Quick Demote Button ke sath)
> • `.demote` - Admin rights revoke karein
> • `.mute` - User ko mute karein (Quick Unmute Button ke sath)
> • `.unmute` - User ko unmute karein
> • `.ban` - Permanently ban karein
> • `.kick` - Group se kick karein
"""

AFK_TEXT = """
> 💤 **AFK (Away From Keyboard) System:**
> 
> • `.afk <reason>` - AFK status set karein
> • Group ke sabhi members ke liye fully functional
> • Mention ya reply karne par bot instant notice dega
> • Wapas aane par automatically disable ho jayega
"""

WELCOMER_TEXT = """
> ✨ **Join Welcomer & Automation:**
> 
> • Pending join requests auto-approval system
> • New users ke aane par custom quote welcome message
> • `.start` - Welcomer automation on karein
> • `.stop` - Welcomer automation pause karein
"""

def start_keyboard(bot_username: str):
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🛡️ Admin Features", callback_data="help_admin"),
            InlineKeyboardButton("💤 AFK System", callback_data="help_afk")
        ],
        [
            InlineKeyboardButton("✨ Join Welcomer", callback_data="help_welcomer")
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
    mention = f"[{message.from_user.first_name}](tg://user?id={message.from_user.id})"
    await message.reply_text(
        text=START_TEXT.format(mention=mention),
        reply_markup=start_keyboard(bot.username)
    )

@Client.on_callback_query()
async def callback_handler(client, query: CallbackQuery):
    data = query.data
    bot = await client.get_me()
    mention = f"[{query.from_user.first_name}](tg://user?id={query.from_user.id})"

    if data == "help_admin":
        await query.message.edit_text(text=ADMIN_TEXT, reply_markup=BACK_KEYBOARD)
    elif data == "help_afk":
        await query.message.edit_text(text=AFK_TEXT, reply_markup=BACK_KEYBOARD)
    elif data == "help_welcomer":
        await query.message.edit_text(text=WELCOMER_TEXT, reply_markup=BACK_KEYBOARD)
    elif data == "help_back":
        await query.message.edit_text(
            text=START_TEXT.format(mention=mention),
            reply_markup=start_keyboard(bot.username)
        )
    await query.answer()
    
