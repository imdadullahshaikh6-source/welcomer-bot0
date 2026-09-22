from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

START_TEXT = """
👋 **Hello {mention}!**

Main ek advance **Group Management Bot** hoon. Mujhe aapke group ko manage karne aur automatically join requests accept karne ke liye banaya gaya hai.

Niche diye gaye buttons par click karke mere features ke baare mein jaanein! 🚀
"""

ADMIN_TEXT = """
🛡️ **Admin Commands & Features:**

• `.promote <title>` - Kisi user ko group ka admin banayein.
• `.demote` - Kisi admin se powers wapas lein.
• `.ban` - User ko permanently group se ban karein.
• `.kick` - User ko group se kick karein.
• `.mute` - User ko text messages bhejne se mute karein.
• `.unmute` - Muted user ko unmute karein.

*(Yeh commands sirf Owner aur Group Admins ke liye hain)*
"""

AFK_TEXT = """
💤 **AFK (Away From Keyboard) System:**

• `.afk <reason>` - AFK mode on karein (e.g. `.afk khana khane`).
• Jab koi aapko group me tag ya reply karega, bot unhein batayega ki aap busy hain.
• Wapas aakar jaise hi aap koi message bhejenge, AFK mode automatically remove ho jayega.

*(Yeh feature group ke sabhi members use kar sakte hain)*
"""

WELCOMER_TEXT = """
✨ **Join Requests & Auto Welcome:**

• Bot group ke pending join requests ko automatically accept karta hai.
• Accept hone ke baad new member ko warm welcome message bhejta hai.
• `.start` - Welcomer automation ko activate karein.
• `.stop` - Automation ko pause/stop karein.

*(Yeh controls sirf Bot Owner ke paas hote hain)*
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

# ==================== /start in Private ====================
@Client.on_message(filters.command("start") & filters.private)
async def private_start(client, message):
    bot = await client.get_me()
    mention = f"[{message.from_user.first_name}](tg://user?id={message.from_user.id})"
    await message.reply_text(
        text=START_TEXT.format(mention=mention),
        reply_markup=start_keyboard(bot.username)
    )

# ==================== Button Clicks (Callbacks) ====================
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
  
