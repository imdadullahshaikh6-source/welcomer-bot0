from pyrogram import Client, filters
from pyrogram.enums import ParseMode
from pyrogram.types import ChatJoinRequest, Message

# Active groups set for auto-accepting requests
active_request_chats = set()

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

    if len(args) < 2:
        current_status = "ON 🟢" if chat_id in active_request_chats else "OFF 🔴"
        return await message.reply_text(
            f"<blockquote>ℹ️ <b>Current Status:</b> <code>{current_status}</code>\n\n"
            "Use: <code>.requestaccept on</code> ya <code>.requestaccept off</code></blockquote>",
            parse_mode=ParseMode.HTML
        )

    mode = args[1].lower()

    if mode in ["on", "enable", "chalu"]:
        if chat_id in active_request_chats:
            return await message.reply_text(
                "<blockquote>⚠️ <b>Auto Request Accept pehle se hi ON hai!</b></blockquote>",
                parse_mode=ParseMode.HTML
            )
        active_request_chats.add(chat_id)
        text = (
            "<blockquote>⚡ <b>𝙧𝙚𝙦𝙪𝙚𝙨𝙩 𝙖𝙘𝙘𝙚𝙥𝙩 : 𝙤𝙣</b> ⚡\n"
            "✦ ━━━━━━━━━━━━━━━━━━ ✦\n"
            f"👮 <b>Updated By:</b> <a href='tg://user?id={message.from_user.id}'>{admin_name}</a>\n"
            "🟢 <b>Status:</b> Enabled\n"
            "📥 Ab aane wali sabhi join requests automatically accept hongi!</blockquote>"
        )
        await message.reply_text(text=text, parse_mode=ParseMode.HTML)

    elif mode in ["off", "disable", "band"]:
        if chat_id not in active_request_chats:
            return await message.reply_text(
                "<blockquote>⚠️ <b>Auto Request Accept pehle se hi OFF hai!</b></blockquote>",
                parse_mode=ParseMode.HTML
            )
        active_request_chats.remove(chat_id)
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

    if chat_id not in active_request_chats:
        return

    try:
        await client.approve_chat_join_request(chat_id=chat_id, user_id=request.from_user.id)
    except Exception:
        pass
        
