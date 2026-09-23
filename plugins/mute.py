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

async def is_admin_or_owner(client: Client, chat_id: int, user_id: int):
    try:
        member = await client.get_chat_member(chat_id, user_id)
        if member.status in [ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR]:
            # Owner ke paas full right hota hai, admin ke privileges check karo
            if member.status == ChatMemberStatus.OWNER:
                return True
            if member.privileges and member.privileges.can_restrict_members:
                return True
        return False
    except Exception:
        return False

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
@Client.on_message(filters.command(["mute", "dmute"], prefixes=[".", "/"]) & filters.group)
async def mute_command(client: Client, message: Message):
    if not message.from_user:
        return

    # Check Admin Right
    can_mute = await is_admin_or_owner(client, message.chat.id, message.from_user.id)
    if not can_mute:
        return await message.reply_text(
            "<blockquote>❌ <b>Permission Denied!</b>\nAapke paas members ko mute/restrict karne ka right nahi hai!</blockquote>",
            parse_mode=ParseMode.HTML,
        )

    target = await extract_target_user(client, message)
    if not target:
        return await message.reply_text(
            "<blockquote>⚠️ <b>Kisi user/bot ke message par reply karein ya tag karein:</b>\n<code>.mute @username</code></blockquote>",
            parse_mode=ParseMode.HTML,
        )

    bot = await client.get_me()
    if target.id == bot.id:
        return await message.reply_text("<blockquote>🥺 Main khud ko mute nahi kar sakti!</blockquote>", parse_mode=ParseMode.HTML)

    # Admin check on target
    try:
        t_member = await client.get_chat_member(message.chat.id, target.id)
        if t_member.status in [ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR]:
            return await message.reply_text("<blockquote>❌ <b>Admin ko mute nahi kiya ja sakta!</b></blockquote>", parse_mode=ParseMode.HTML)
    except Exception:
        pass

    try:
        # User message permissions band karna
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
            f"<blockquote>⚠️ <b>Failed to mute:</b> <code>{html.escape(str(e))}</code></blockquote>",
            parse_mode=ParseMode.HTML,
        )

# ==================== UNMUTE (COMMAND) ====================
@Client.on_message(filters.command(["unmute"], prefixes=[".", "/"]) & filters.group)
async def unmute_command(client: Client, message: Message):
    if not message.from_user:
        return

    can_unmute = await is_admin_or_owner(client, message.chat.id, message.from_user.id)
    if not can_unmute:
        return await message.reply_text(
            "<blockquote>❌ <b>Permission Denied!</b>\nAapke paas members ko unmute karne ka right nahi hai!</blockquote>",
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
            f"💬 <i>Ab messages bhej sakte hain!</i></blockquote>",
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

    can_unmute = await is_admin_or_owner(client, chat_id, query.from_user.id)
    if not can_unmute:
        return await query.answer("❌ Sirf Admins hi yeh button use kar sakte hain!", show_alert=True)

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
        
