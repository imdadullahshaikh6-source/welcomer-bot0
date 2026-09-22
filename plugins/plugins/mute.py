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

async def get_admin_privileges(client: Client, user_id: int, chat_id: int):
    try:
        m = await client.get_chat_member(chat_id, user_id)
        if m.status == ChatMemberStatus.OWNER:
            return True, "owner"
        if m.status == ChatMemberStatus.ADMINISTRATOR:
            return True, m.privileges
        return False, None
    except Exception:
        return False, None

async def extract_target_user(client: Client, message: Message):
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
@Client.on_message(filters.command(["mute"], prefixes=[".", "/"]) & filters.group)
async def mute_command(client: Client, message: Message):
    if not message.from_user:
        return

    is_adm, privs = await get_admin_privileges(client, message.from_user.id, message.chat.id)
    if not is_adm:
        return

    # Check Restrict Members Permission
    if privs != "owner" and not (privs and privs.can_restrict_members):
        return await message.reply_text(
            "<blockquote>❌ <b>Permission Denied!</b>\n"
            "Aapke paas members ko mute karne ka right (Ban Users) nahi hai!</blockquote>",
            parse_mode=ParseMode.HTML,
        )

    target = await extract_target_user(client, message)
    if not target:
        return await message.reply_text(
            "<blockquote>⚠️ <b>User par reply karein ya tag karein:</b>\n<code>.mute @username</code></blockquote>",
            parse_mode=ParseMode.HTML,
        )

    bot = await client.get_me()
    if target.id == bot.id:
        return await message.reply_text("<blockquote>🥺 Main khud ko mute nahi kar sakti!</blockquote>", parse_mode=ParseMode.HTML)

    target_is_adm, _ = await get_admin_privileges(client, target.id, message.chat.id)
    if target_is_adm:
        return await message.reply_text("<blockquote>❌ <b>Admin ko mute nahi kiya ja sakta!</b></blockquote>", parse_mode=ParseMode.HTML)

    try:
        await client.restrict_chat_member(
            chat_id=message.chat.id,
            user_id=target.id,
            permissions=ChatPermissions(can_send_messages=False),
        )
        mention = get_user_mention(target)
        btn = InlineKeyboardMarkup([[InlineKeyboardButton("🔊 Unmute Member", callback_data=f"adm_unmute_{target.id}")]])

        await message.reply_text(
            f"<blockquote>🤐 <b>Muted!</b>\n"
            f"✦ ━━━━━━━━━━━━━━━━━━ ✦\n"
            f"👤 <b>User:</b> {mention}\n"
            f"🔇 <i>Message permissions band kar di gayi hain!</i></blockquote>",
            reply_markup=btn,
            parse_mode=ParseMode.HTML,
        )
    except Exception as e:
        await message.reply_text(
            f"<blockquote>⚠️ <b>Failed to mute:</b> <code>{html.escape(str(e))}</code></blockquote>",
            parse_mode=ParseMode.HTML,
        )

# ==================== UNMUTE (COMMAND) ====================
@Client.on_message(filters.command(["unmute"], prefixes=[".", "/"]) & filters.group)
async def unmute_command(client: Client, message: Message):
    if not message.from_user:
        return

    is_adm, privs = await get_admin_privileges(client, message.from_user.id, message.chat.id)
    if not is_adm:
        return

    # Check Restrict Members Permission
    if privs != "owner" and not (privs and privs.can_restrict_members):
        return await message.reply_text(
            "<blockquote>❌ <b>Permission Denied!</b>\n"
            "Aapke paas members ko unmute karne ka right (Ban Users) nahi hai!</blockquote>",
            parse_mode=ParseMode.HTML,
        )

    target = await extract_target_user(client, message)
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
            f"💬 <i>Restrictions hata di gayi hain, ab messages bhej sakte hain!</i></blockquote>",
            parse_mode=ParseMode.HTML,
        )
    except Exception as e:
        await message.reply_text(
            f"<blockquote>⚠️ <b>Failed to unmute:</b> <code>{html.escape(str(e))}</code></blockquote>",
            parse_mode=ParseMode.HTML,
        )

# ==================== UNMUTE (BUTTON CALLBACK) ====================
@Client.on_callback_query(filters.regex(r"^adm_unmute_(\d+)$"))
async def unmute_button_callback(client: Client, query: CallbackQuery):
    target_id = int(query.data.split("_")[2])
    chat_id = query.message.chat.id

    is_adm, privs = await get_admin_privileges(client, query.from_user.id, chat_id)
    if not is_adm:
        return await query.answer("❌ Sirf Admins hi yeh button use kar sakte hain!", show_alert=True)

    # Check Restrict Members Permission on Button Click
    if privs != "owner" and not (privs and privs.can_restrict_members):
        return await query.answer("❌ Aapke paas members ko unmute karne ka right nahi hai!", show_alert=True)

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
          
