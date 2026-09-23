import html
from pyrogram import Client, filters
from pyrogram.enums import ParseMode, ChatMemberStatus
from pyrogram.errors import RPCError

async def is_user_admin(client: Client, chat_id: int, user_id: int) -> bool:
    try:
        m = await client.get_chat_member(chat_id, user_id)
        if m.status in [ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR]:
            return True
        return False
    except Exception:
        # Fallback true taaki false-rejection na ho
        return True

@Client.on_message(filters.command(["pin", "unpin"], prefixes=[".", "/"]) & filters.group)
async def pin_unpin_handler(client: Client, message):
    chat_id = message.chat.id

    # 1. Check Bot's own rights
    try:
        me = await client.get_chat_member(chat_id, "me")
        if me.status not in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
            return await message.reply_text(
                "<blockquote>⚠️ <b>I am not Admin!</b>\n"
                "Mujhe message pin karne ke liye pehle group me Admin banayein!</blockquote>",
                parse_mode=ParseMode.HTML
            )
        if me.status == ChatMemberStatus.ADMINISTRATOR and me.privileges and not me.privileges.can_pin_messages:
            return await message.reply_text(
                "<blockquote>⚠️ <b>Permission Missing!</b>\n"
                "Mere paas <b>'Pin Messages'</b> ka right band hai. Kripya admin settings me jaakar use allow karein!</blockquote>",
                parse_mode=ParseMode.HTML
            )
    except Exception as e:
        pass

    # 2. Check Sender's admin status
    sender_id = message.from_user.id if message.from_user else (message.sender_chat.id if message.sender_chat else 0)
    if message.sender_chat and message.sender_chat.id == chat_id:
        is_adm = True
    else:
        is_adm = await is_user_admin(client, chat_id, sender_id)

    if not is_adm:
        return await message.reply_text(
            "<blockquote>❌ <b>Permission Denied!</b>\nSirf group Admins hi message pin/unpin kar sakte hain!</blockquote>",
            parse_mode=ParseMode.HTML
        )

    # 3. Check Reply
    if not message.reply_to_message:
        return await message.reply_text(
            "<blockquote>⚠️ <b>Usage:</b> Jis message ko pin ya unpin karna hai, uspar reply karke <code>.pin</code> ya <code>.unpin</code> likhein!</blockquote>",
            parse_mode=ParseMode.HTML
        )

    cmd = message.command[0].lower()
    target_msg_id = message.reply_to_message.id

    try:
        if cmd == "pin":
            await client.pin_chat_message(
                chat_id=chat_id,
                message_id=target_msg_id,
                both_sides=True
            )
            await message.reply_text(
                "<blockquote>📌 <b>Message successfully pinned!</b></blockquote>",
                parse_mode=ParseMode.HTML
            )
        else:
            await client.unpin_chat_message(
                chat_id=chat_id,
                message_id=target_msg_id
            )
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
            f"<blockquote>⚠️ <b>Pin Failed:</b> <code>{html.escape(str(e))}</code></blockquote>",
            parse_mode=ParseMode.HTML
        )
        
