import html
from pyrogram import Client, filters
from pyrogram.enums import ParseMode, ChatMemberStatus
from pyrogram.errors import RPCError

async def scan_bot_pin_permissions(client: Client, chat_id: int):
    """
    Scans bot's actual admin status and specific 'can_pin_messages' right.
    Returns: (status: bool, error_code: str)
    """
    try:
        me = await client.get_chat_member(chat_id, "me")
        if me.status == ChatMemberStatus.OWNER:
            return True, "ok"
        if me.status == ChatMemberStatus.ADMINISTRATOR:
            if me.privileges and me.privileges.can_pin_messages:
                return True, "ok"
            return False, "no_permission"
        return False, "not_admin"
    except Exception:
        return False, "not_admin"

async def check_admin_sender(client: Client, message):
    if message.sender_chat and message.sender_chat.id == message.chat.id:
        return True, True
    if not message.from_user:
        return False, False
    try:
        m = await client.get_chat_member(message.chat.id, message.from_user.id)
        if m.status == ChatMemberStatus.OWNER:
            return True, True
        if m.status == ChatMemberStatus.ADMINISTRATOR:
            can_pin = bool(m.privileges and m.privileges.can_pin_messages)
            return True, can_pin
    except Exception:
        return True, True
    return False, False

@Client.on_message(filters.command(["pin", "unpin"], prefixes=[".", "/"]) & filters.group)
async def pin_unpin_command(client: Client, message):
    # 1. SCAN BOT ADMIN & PIN PERMISSION
    bot_has_right, bot_reason = await scan_bot_pin_permissions(client, message.chat.id)
    if not bot_has_right:
        if bot_reason == "not_admin":
            return await message.reply_text(
                "<blockquote>⚠️ <b>I am not Admin!</b>\n"
                "Is command ko chalane ke liye pehle mujhe group me Admin banayein!</blockquote>",
                parse_mode=ParseMode.HTML
            )
        elif bot_reason == "no_permission":
            return await message.reply_text(
                "<blockquote>⚠️ <b>Permission Missing!</b>\n"
                "Main group me admin hoon, lekin mere paas <b>'Pin Messages'</b> ka right band hai. Kripya mujhe permission dein!</blockquote>",
                parse_mode=ParseMode.HTML
            )

    # 2. SCAN SENDER ADMIN & PIN PERMISSION
    is_admin, can_pin = await check_admin_sender(client, message)
    if not is_admin:
        return await message.reply_text(
            "<blockquote>❌ <b>Permission Denied!</b>\nSirf group Admins hi message pin/unpin kar sakte hain!</blockquote>",
            parse_mode=ParseMode.HTML
        )
    if not can_pin:
        return await message.reply_text(
            "<blockquote>❌ <b>Permission Denied!</b>\nAapke paas 'Pin Messages' ka right nahi hai!</blockquote>",
            parse_mode=ParseMode.HTML
        )

    # 3. REPLY CHECK
    if not message.reply_to_message:
        return await message.reply_text(
            "<blockquote>⚠️ <b>Usage:</b> Jis message ko pin ya unpin karna hai, uspar reply karke <code>.pin</code> ya <code>.unpin</code> likhein!</blockquote>",
            parse_mode=ParseMode.HTML
        )

    cmd = message.command[0].lower()
    try:
        if cmd == "pin":
            # notify parameter False rakhte hain taaki members spam na ho
            await message.reply_to_message.pin(both_sides=True)
            await message.reply_text(
                "<blockquote>📌 <b>Message successfully pinned!</b></blockquote>",
                parse_mode=ParseMode.HTML
            )
        else:
            await message.reply_to_message.unpin()
            await message.reply_text(
                "<blockquote>📌 <b>Message successfully unpinned!</b></blockquote>",
                parse_mode=ParseMode.HTML
            )
    except RPCError as tg_err:
        await message.reply_text(
            f"<blockquote>❌ <b>Telegram Error:</b> <code>{html.escape(tg_err.MESSAGE)}</code></blockquote>",
            parse_mode=ParseMode.HTML
        )
    except Exception as e:
        await message.reply_text(
            f"<blockquote>⚠️ <b>Failed:</b> <code>{html.escape(str(e))}</code></blockquote>",
            parse_mode=ParseMode.HTML
        )
      
