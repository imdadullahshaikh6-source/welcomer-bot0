from pyrogram import Client, filters
from pyrogram.enums import ParseMode
from pyrogram.types import ChatJoinRequest, Message

active_accept_chats = set()

async def is_admin(client: Client, user_id: int, chat_id: int) -> bool:
    try:
        member = await client.get_chat_member(chat_id, user_id)
        return member.status.name in ["OWNER", "ADMINISTRATOR"]
    except Exception:
        return False

# ==================== .uthao ====================
@Client.on_message(filters.command(["uthao"], prefixes=[".", "/"]) & filters.group)
async def uthao_cmd(client: Client, message: Message):
    if not message.from_user or not await is_admin(client, message.from_user.id, message.chat.id):
        return

    chat_id = message.chat.id
    if chat_id in active_accept_chats:
        return await message.reply_text(
            "<blockquote>⚠️ <b>Join Request acceptance pehle se hi chalu hai!</b></blockquote>",
            parse_mode=ParseMode.HTML
        )

    active_accept_chats.add(chat_id)
    admin_name = message.from_user.first_name or "Admin"

    text = (
        "<blockquote>⚡ <b>𝙟𝙤𝙞𝙣 𝙧𝙚𝙦𝙪𝙚𝙨𝙩𝙨 𝙖𝙘𝙩𝙞𝙫𝙖𝙩𝙚𝙙</b> ⚡\n"
        "✦ ━━━━━━━━━━━━━━━━━━ ✦\n"
        f"👮 <b>Activated By:</b> <a href='tg://user?id={message.from_user.id}'>{admin_name}</a>\n"
        "🟢 <b>Status:</b> Ab aane wali sabhi join requests turant approve hongi!\n"
        "🛑 <i>Rokne ke liye <code>.ruko</code> likhein.</i></blockquote>"
    )
    await message.reply_text(text=text, parse_mode=ParseMode.HTML)

# ==================== .ruko ====================
@Client.on_message(filters.command(["ruko"], prefixes=[".", "/"]) & filters.group)
async def ruko_cmd(client: Client, message: Message):
    if not message.from_user or not await is_admin(client, message.from_user.id, message.chat.id):
        return

    chat_id = message.chat.id
    if chat_id not in active_accept_chats:
        return await message.reply_text(
            "<blockquote>⚠️ <b>Join Request acceptance abhi band hi hai!</b></blockquote>",
            parse_mode=ParseMode.HTML
        )

    active_accept_chats.remove(chat_id)
    admin_name = message.from_user.first_name or "Admin"

    text = (
        "<blockquote>🛑 <b>𝙟𝙤𝙞𝙣 𝙧𝙚𝙦𝙪𝙚𝙨𝙩𝙨 𝙨𝙩𝙤𝙥𝙥𝙚𝙙</b> 🛑\n"
        "✦ ━━━━━━━━━━━━━━━━━━ ✦\n"
        f"👮 <b>Stopped By:</b> <a href='tg://user?id={message.from_user.id}'>{admin_name}</a>\n"
        "🔴 <b>Status:</b> Join requests auto-accept hona band ho gaya hai.</blockquote>"
    )
    await message.reply_text(text=text, parse_mode=ParseMode.HTML)

# ==================== Auto-Accept Handler ====================
@Client.on_chat_join_request()
async def auto_accept_handler(client: Client, request: ChatJoinRequest):
    chat_id = request.chat.id

    if chat_id not in active_accept_chats:
        return

    try:
        await client.approve_chat_join_request(chat_id=chat_id, user_id=request.from_user.id)

        user = request.from_user
        first_name = user.first_name or "New Member"
        mention = f"<a href='tg://user?id={user.id}'>{first_name}</a>"

        welcome_text = (
            "<blockquote>✨ <b>𝙬𝙚𝙡𝙘𝙤𝙢𝙚 𝙩𝙤 𝙩𝙝𝙚 𝙛𝙖𝙢𝙞𝙡𝙮</b> ✨\n"
            "✦ ━━━━━━━━━━━━━━━━━━ ✦\n"
            f"👋 Hello {mention}!\n"
            "🎉 Aapka join request <b>Approve</b> kar diya gaya hai.\n"
            "💬 Rules follow karein aur chat enjoy karein!</blockquote>"
        )

        await client.send_message(
            chat_id=chat_id,
            text=welcome_text,
            parse_mode=ParseMode.HTML
        )
    except Exception:
        pass
        
