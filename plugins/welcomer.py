from pyrogram import Client, filters
from pyrogram.enums import ParseMode
from pyrogram.types import ChatJoinRequest, Message
from database import is_request_accept_on, set_request_accept

async def is_admin(client: Client, user_id: int, chat_id: int) -> bool:
    try:
        member = await client.get_chat_member(chat_id, user_id)
        return member.status.name in ["OWNER", "ADMINISTRATOR"]
    except Exception:
        return False

# ==================== .requestaccept on/off ====================
@Client.on_message(filters.command(["requestaccept"], prefixes=[".", "/"]) & filters.group)
async def request_accept_toggle(client: Client, message: Message):
    if not message.from_user or not await is_admin(client, message.from_user.id, message.chat.id):
        return

    chat_id = message.chat.id
    admin_name = message.from_user.first_name or "Admin"
    args = message.text.split()
    current_status_db = await is_request_accept_on(chat_id)

    if len(args) < 2:
        status_text = "ON 🟢" if current_status_db else "OFF 🔴"
        return await message.reply_text(
            f"<blockquote>ℹ️ <b>Current Status:</b> <code>{status_text}</code>\n\n"
            "Use: <code>.requestaccept on</code> ya <code>.requestaccept off</code></blockquote>",
            parse_mode=ParseMode.HTML
        )

    mode = args[1].lower()

    if mode in ["on", "enable", "chalu"]:
        if current_status_db:
            return await message.reply_text(
                "<blockquote>⚠️ <b>Auto Request Accept pehle se hi ON hai!</b></blockquote>",
                parse_mode=ParseMode.HTML
            )
        await set_request_accept(chat_id, True)
        text = (
            "<blockquote>⚡ <b>𝙧𝙚𝙦𝙪𝙚𝙨𝙩 𝙖𝙘𝙘𝙚𝙥𝙩 : 𝙤𝙣</b> ⚡\n"
            "✦ ━━━━━━━━━━━━━━━━━━ ✦\n"
            f"👮 <b>Updated By:</b> <a href='tg://user?id={message.from_user.id}'>{admin_name}</a>\n"
            "🟢 <b>Status:</b> Enabled\n"
            "📥 Ab aane wali sabhi join requests automatically accept hongi!</blockquote>"
        )
        await message.reply_text(text=text, parse_mode=ParseMode.HTML)

    elif mode in ["off", "disable", "band"]:
        if not current_status_db:
            return await message.reply_text(
                "<blockquote>⚠️ <b>Auto Request Accept pehle se hi OFF hai!</b></blockquote>",
                parse_mode=ParseMode.HTML
            )
        await set_request_accept(chat_id, False)
        text = (
            "<blockquote>🛑 <b>𝙧𝙚𝙦𝙪𝙚𝙨𝙩 𝙖𝙘𝙘𝙚𝙥𝙩 : 𝙤𝙛𝙛</b> 🛑\n"
            "✦ ━━━━━━━━━━━━━━━━━━ ✦\n"
            f"👮 <b>Updated By:</b> <a href='tg://user?id={message.from_user.id}'>{admin_name}</a>\n"
            "🔴 <b>Status:</b> Disabled\n"
            "📥 Nayi join requests automatically accept hona band ho gayi hain.</blockquote>"
        )
        await message.reply_text(text=text, parse_mode=ParseMode.HTML)

    else:
        await message.reply_text(
            "<blockquote>⚠️ <b>Invalid option!</b>\nUse: <code>.requestaccept on</code> ya <code>.requestaccept off</code></blockquote>",
            parse_mode=ParseMode.HTML
        )

# ==================== Live Join Request Acceptor ====================
@Client.on_chat_join_request()
async def auto_accept_listener(client: Client, request: ChatJoinRequest):
    chat_id = request.chat.id

    if not await is_request_accept_on(chat_id):
        return

    try:
        await client.approve_chat_join_request(chat_id=chat_id, user_id=request.from_user.id)
    except Exception:
        pass
        
