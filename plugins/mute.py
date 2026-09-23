import html
from pyrogram import Client, filters
from pyrogram.enums import ParseMode, ChatMemberStatus, MessageEntityType
from pyrogram.types import (
    Message,
    CallbackQuery,
    ChatPermissions,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

async def check_admin_rights(client: Client, message: Message):
    # Agar user anonymous admin hai (channel ke roop me bhej raha hai)
    if message.sender_chat and message.sender_chat.id == message.chat.id:
        return True, True

    if not message.from_user:
        return False, False

    try:
        member = await client.get_chat_member(message.chat.id, message.from_user.id)
        if member.status == ChatMemberStatus.OWNER:
            return True, True
        if member.status == ChatMemberStatus.ADMINISTRATOR:
            can_restrict = bool(member.privileges and member.privileges.can_restrict_members)
            return True, can_restrict
    except Exception:
        pass
    return False, False

async def extract_target(client: Client, message: Message):
    if message.reply_to_message:
        if message.reply_to_message.from_user:
            return message.reply_to_message.from_user
        if message.reply_to_message.sender_chat:
            return message.reply_to_message.sender_chat

    if message.entities:
        for ent in message.entities:
            if ent.type == MessageEntityType.TEXT_MENTION and ent.user:
                return ent.user
            if ent.type == MessageEntityType.MENTION:
                raw_u = message.text[ent.offset : ent.offset + ent.length]
                try:
                    return await client.get_users(raw_u)
                except Exception:
                    pass

    parts = message.text.split(maxsplit=2)
    if len(parts) > 1:
        arg = parts[1].strip()
        try:
            val = int(arg) if (arg.isdigit() or arg.startswith("-100")) else arg
            return await client.get_users(val)
        except Exception:
            return None
    return None

def get_user_mention(user):
    if hasattr(user, "first_name"):
        name = html.escape(user.first_name or "User")
        return f"<a href='tg://user?id={user.id}'>{name}</a>"
    if hasattr(user, "title"):
        return f"<b>{html.escape(user.title)}</b>"
    return "User"

# ==================== MUTE ====================
@Client.on_message(filters.command(["mute", "dmute"], prefixes=[".", "/"]) & filters.group)
async def mute_command(client: Client, message: Message):
    is_adm, can_restrict = await check_admin_rights(client, message)
    if not is_adm:
        return

    if not can_restrict:
        return await message.reply_text(
            "<blockquote>❌ <b>Permission Denied!</b>\nAapke paas members ko mute/restrict karne ka right nahi hai!</blockquote>",
            parse_mode=ParseMode.HTML,
        )

    target = await extract_target(client, message)
    if not target:
        return await message.reply_text(
            "<blockquote>⚠️ <b>Kisi user ke message par reply karke ya tag karke command dein:</b>\n<code>.mute @username</code></blockquote>",
            parse_mode=ParseMode.HTML,
        )

    bot = await client.get_me()
    if target.id == bot.id:
        return await message.reply_text("<blockquote>🥺 Main khud ko mute nahi kar sakti!</blockquote>", parse_mode=ParseMode.HTML)

    # Check if target is admin
    try:
        t_member = await client.get_chat_member(message.chat.id, target.id)
        if t_member.status in [ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR]:
            return await message.reply_text("<blockquote>❌ <b>Admin ko mute nahi kiya ja sakta!</b></blockquote>", parse_mode=ParseMode.HTML)
    except Exception:
        pass

    try:
        await client.restrict_chat_member(
            chat_id=message.chat.id,
            user_id=target.id,
            permissions=ChatPermissions(can_send_messages=False),
        )

        if message.command[0].lower() == "dmute" and message.reply_to_message:
            try:
                await message.reply_to_message.delete()
            except Exception:
                pass

        mention = get_user_mention(target)
        btn = InlineKeyboardMarkup([[InlineKeyboardButton("🔊 Unmute Member", callback_data=f"adm_unmute_{target.id}")]])

        await message.reply_text(
            f"<blockquote>🤐 <b>Muted!</b>\n"
            f"✦ ━━━━━━━━━━━━━━━━━━ ✦\n"
            f"👤 <b>User:</b> {mention} [<code>{target.id}</code>]\n"
            f"🔇 <i>Message permissions band kar di gayi hain!</i></blockquote>",
            reply_markup=btn,
            parse_mode=ParseMode.HTML,
        )
    except Exception as e:
        await message.reply_text(
            f"<blockquote>⚠️ <b>Failed to mute:</b> <code>{html.escape(str(e))}</code>\n\n<i>Kripya check karein ki Bot ke paas group me 'Ban Users' ka right hai ya nahi!</i></blockquote>",
            parse_mode=ParseMode.HTML,
        )

# ==================== UNMUTE ====================
@Client.on_message(filters.command(["unmute"], prefixes=[".", "/"]) & filters.group)
async def unmute_command(client: Client, message: Message):
    is_adm, can_restrict = await check_admin_rights(client, message)
    if not is_adm or not can_restrict:
        return

    target = await extract_target(client, message)
    if not target:
        return await message.reply_text(
            "<blockquote>⚠️ <b>User par reply karein ya tag karein:</b>\n<code>.unmute @username</code></blockquote>",
            parse_mode=ParseMode.HTML,
        )

    try:
        chat = await client.get_chat(message.chat.id)
        default_perms = chat.permissions or ChatPermissions(
            can_send_messages=True,
            can_send_media_messages=True,
            can_send_other_messages=True,
            can_add_web_page_previews=True,
        )
        await client.restrict_chat_member(
            chat_id=message.chat.id,
            user_id=target.id,
            permissions=default_perms,
        )
        mention = get_user_mention(target)
        await message.reply_text(
            f"<blockquote>🔊 <b>Unmuted!</b>\n"
            f"✦ ━━━━━━━━━━━━━━━━━━ ✦\n"
            f"👤 <b>User:</b> {mention}\n"
            f"💬 <i>Ab messages bhej sakte hain!</i></blockquote>",
            parse_mode=ParseMode.HTML,
        )
    except Exception as e:
        await message.reply_text(
            f"<blockquote>⚠️ <b>Failed to unmute:</b> <code>{html.escape(str(e))}</code></blockquote>",
            parse_mode=ParseMode.HTML,
        )

# ==================== UNMUTE BUTTON CALLBACK ====================
@Client.on_callback_query(filters.regex(r"^adm_unmute_(\d+)$"))
async def unmute_button_callback(client: Client, query: CallbackQuery):
    target_id = int(query.data.split("_")[2])
    chat_id = query.message.chat.id

    try:
        member = await client.get_chat_member(chat_id, query.from_user.id)
        if member.status not in [ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR]:
            return await query.answer("❌ Sirf Admins hi yeh button use kar sakte hain!", show_alert=True)
    except Exception:
        return await query.answer("❌ Error checking admin rights!", show_alert=True)

    try:
        chat = await client.get_chat(chat_id)
        default_perms = chat.permissions or ChatPermissions(
            can_send_messages=True,
            can_send_media_messages=True,
            can_send_other_messages=True,
            can_add_web_page_previews=True,
        )
        await client.restrict_chat_member(chat_id, target_id, default_perms)
        await query.answer("🔊 User unmuted successfully!")

        admin_name = html.escape(query.from_user.first_name)
        await query.message.edit_text(
            f"<blockquote>🔊 <b>Unmuted!</b>\n"
            f"✦ ━━━━━━━━━━━━━━━━━━ ✦\n"
            f"✨ <i>User unmuted by <a href='tg://user?id={query.from_user.id}'>{admin_name}</a>!</i></blockquote>",
            parse_mode=ParseMode.HTML,
        )
    except Exception as e:
        await query.answer(f"Error: {e}", show_alert=True)
        
