import os
from pyrogram import Client, filters
from pyrogram.enums import ParseMode
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

OWNER_USERNAME = "Ownerbackk"
SUPPORT_GROUP_URL = "https://t.me/+UCmLt1cgPhI1MjFl"

START_TEXT = (
    "<blockquote>👑 <b>Hello {mention}!!</b>\n\n"
    "Main aapka <b>All-in-One Group Manager Bot</b> hoon.\n"
    "Groups ko manage karne, custom greetings dene,\n"
    "aur chat environment ko smooth rakhne ke liye tayar hoon!\n\n"
    f"👑 <b>OWNER:</b> @{OWNER_USERNAME}\n\n"
    "Niche diye gaye buttons se explore karein:</blockquote>"
)

HELP_TEXT = (
    "<blockquote>⚡ <b>𝙗𝙤𝙩 𝙘𝙤𝙢𝙢𝙖𝙣𝙙𝙨 𝙢𝙚𝙣𝙪</b> ⚡\n"
    "✦ ━━━━━━━━━━━━━━━━━━ ✦\n"
    "⚙️ <b>Greetings (Admin Only):</b>\n"
    "• <code>.setwelcome</code> - Message/Media par reply karke custom welcome set karein\n"
    "• <code>.welcome on/off</code> - Greetings chalu ya band karein\n"
    "• <code>.getwelcome</code> - Current welcome message preview karein\n"
    "• <code>.resetwelcome</code> - Default welcome par reset karein\n\n"
    "🛡️ <b>Admin Controls:</b>\n"
    "• <code>.promote &lt;title&gt;</code> - User ko admin banayein\n"
    "• <code>.demote</code> - Admin rights hatayein\n"
    "• <code>.mute</code> / <code>.unmute</code> - Member ko mute ya unmute karein\n"
    "• <code>.ban</code> / <code>.kick</code> - Group se nikalen\n"
    "• <code>.pin</code> / <code>.unpin</code> / <code>.unpinall</code> - Messages pin/unpin karein</blockquote>"
)

def get_start_buttons(bot_username: str):
    owner_url = f"https://t.me/{OWNER_USERNAME}"
    add_bot_url = f"https://t.me/{bot_username}?startgroup=true"
    
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("⚡ COMMANDS", callback_data="open_commands")
        ],
        [
            InlineKeyboardButton("👑 OWNER", url=owner_url),
            InlineKeyboardButton("✨ ADD ME", url=add_bot_url)
        ],
        [
            InlineKeyboardButton("💬 SUPPORT", url=SUPPORT_GROUP_URL)
        ]
    ])

@Client.on_message(filters.command("start") & filters.private)
async def start_handler(client: Client, message: Message):
    bot = await client.get_me()
    first_name = message.from_user.first_name or "User"
    mention = f"<a href='tg://user?id={message.from_user.id}'>{first_name}</a>"
    
    caption = START_TEXT.format(mention=mention)
    markup = get_start_buttons(bot.username)
    
    await message.reply_text(
        text=caption,
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True,
        reply_markup=markup
    )

@Client.on_callback_query(filters.regex("^open_commands$"))
async def commands_callback(client: Client, query: CallbackQuery):
    back_markup = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("💬 SUPPORT GROUP", url=SUPPORT_GROUP_URL)
        ],
        [
            InlineKeyboardButton("🔙 BACK", callback_data="back_to_start")
        ]
    ])
    await query.message.edit_text(
        text=HELP_TEXT,
        parse_mode=ParseMode.HTML,
        reply_markup=back_markup
    )
    await query.answer()

@Client.on_callback_query(filters.regex("^back_to_start$"))
async def back_start_callback(client: Client, query: CallbackQuery):
    bot = await client.get_me()
    first_name = query.from_user.first_name or "User"
    mention = f"<a href='tg://user?id={query.from_user.id}'>{first_name}</a>"
    caption = START_TEXT.format(mention=mention)
    markup = get_start_buttons(bot.username)
    
    await query.message.edit_text(
        text=caption,
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True,
        reply_markup=markup
    )
    await query.answer()
    
