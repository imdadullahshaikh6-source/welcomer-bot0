import html
from pyrogram import Client, filters
from pyrogram.enums import ParseMode, ChatMemberStatus, MessageEntityType
from pyrogram.types import (
    Message,
    CallbackQuery,
    ChatPrivileges,
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

# ==================== PROMOTE ====================
@Client.on_message(filters.command(["promote"], prefixes=[".", "/"]) & filters.group)
async def promote_command(client: Client, message: Message):
    if not message.from_user:
        return

    is_adm, privs = await get_admin_privileges(client, message.from_user.id, message.chat.id)
    if not is_adm:
        return

    if privs != "owner" and not (privs and privs.can_promote_members):
        return await message.reply_text(
            "<blockquote>❌ <b>Permission Denied!</b>\nAapke paas new admins promote karne ka right nahi hai!</blockquote>",
            parse_mode=ParseMode.HTML,
        )

    target = await extract_target_user(client, message)
    if not target:
        return await message.reply_text(
            "<blockquote>⚠️ <b>User par reply karein ya tag karein:</b>\n<code>.promote @username &lt;title&gt;</code></blockquote>",
            parse_mode=ParseMode.HTML,
        )

    bot = await client.get_me()
    if target.id == bot.id:
        return await message.reply_text("<blockquote>🥺 Main pehle se bot admin hoon!</blockquote>", parse_mode=ParseMode.HTML)

    parts = message.text.split(maxsplit=2)
    custom_title = "Admin"
    if message.reply_to_message:
        if len(parts) > 1:
            custom_title = message.text.split(maxsplit=1)[1]
    else:
        if len(parts) > 2:
            custom_title = parts[2]

    try:
        p_rights = ChatPrivileges(
            can_manage_chat=True,
            can_delete_messages=True,
            can_manage_video_chats=True,
            can_restrict_members=True,
            can_promote_members=False,
            can_change_info=True,
            can_invite_users=True,
            can_pin_messages=True,
        )
        await client.promote_chat_member(message.chat.id, target.id, p_rights)
        try:
            await client.set_administrator_title(message.chat.id, target.id, custom_title[:16])
        except Exception:
            pass

        mention = get_user_mention(target)
        btn = InlineKeyboardMarkup([[InlineKeyboardButton("🔻 Demote Admin", callback_data=f"adm_demote_{target.id}")]])

        await message.reply_text(
            f"<blockquote>🎖️ <b>Promoted!</b>\n"
            f"✦ ━━━━━━━━━━━━━━━━━━ ✦\n"
            f"👤 <b>Admin:</b> {mention}\n"
            f"🏷️ <b>Title:</b> <code>{html.escape(custom_title)}</code>\n"
            f"✨ <i>Admin privileges successfully granted!</i></blockquote>",
            reply_markup=btn,
            parse_mode=ParseMode.HTML,
        )
    except Exception as e:
        await message.reply_text(
            f"<blockquote>⚠️ <b>Failed to promote:</b> <code>{html.escape(str(e))}</code></blockquote>",
            parse_mode=ParseMode.HTML,
        )

# ==================== DEMOTE ====================
@Client.on_message(filters.command(["demote"], prefixes=[".", "/"]) & filters.group)
async def demote_command(client: Client, message: Message):
    if not message.from_user:
        return

    is_adm, privs = await get_admin_privileges(client, message.from_user.id, message.chat.id)
    if not is_adm:
        return

    if privs != "owner" and not (privs and privs.can_promote_members):
        return await message.reply_text(
            "<blockquote>❌ <b>Permission Denied!</b>\nAapke paas admins demote karne ka right nahi hai!</blockquote>",
            parse_mode=ParseMode.HTML,
        )

    target = await extract_target_user(client, message)
    if not target:
        return await message.reply_text(
            "<blockquote>⚠️ <b>User par reply karein ya tag karein:</b> <code>.demote @username</code></blockquote>",
            parse_mode=ParseMode.HTML,
        )

    bot = await client.get_me()
    if target.id == bot.id:
        return await message.reply_text("<blockquote>🥺 Main khud ko demote nahi kar sakti!</blockquote>", parse_mode=ParseMode.HTML)

    try:
        no_rights = ChatPrivileges(
            can_manage_chat=False,
            can_delete_messages=False,
            can_manage_video_chats=False,
            can_restrict_members=False,
            can_promote_members=False,
            can_change_info=False,
            can_invite_users=False,
            can_pin_messages=False,
        )
        await client.promote_chat_member(message.chat.id, target.id, no_rights)
        mention = get_user_mention(target)
        await message.reply_text(
            f"<blockquote>🔻 <b>Demoted!</b>\n"
            f"✦ ━━━━━━━━━━━━━━━━━━ ✦\n"
            f"👤 <b>User:</b> {mention}\n"
            f"✨ <i>Admin rights revoked successfully!</i></blockquote>",
            parse_mode=ParseMode.HTML,
        )
    except Exception as e:
        await message.reply_text(
            f"<blockquote>⚠️ <b>Failed to demote:</b> <code>{html.escape(str(e))}</code></blockquote>",
            parse_mode=ParseMode.HTML,
        )

# Button Callback Demote
@Client.on_callback_query(filters.regex(r"^adm_demote_(\d+)$"))
async def demote_button_callback(client: Client, query: CallbackQuery):
    target_id = int(query.data.split("_")[2])
    chat_id = query.message.chat.id

    is_adm, privs = await get_admin_privileges(client, query.from_user.id, chat_id)
    if not is_adm:
        return await query.answer("❌ Sirf Admins hi yeh button use kar sakte hain!", show_alert=True)

    if privs != "owner" and not (privs and privs.can_promote_members):
        return await query.answer("❌ Aapke paas admins demote karne ka right nahi hai!", show_alert=True)

    try:
        no_rights = ChatPrivileges(
            can_manage_chat=False,
            can_delete_messages=False,
            can_manage_video_chats=False,
            can_restrict_members=False,
            can_promote_members=False,
            can_change_info=False,
            can_invite_users=False,
            can_pin_messages=False,
        )
        await client.promote_chat_member(chat_id, target_id, no_rights)
        await query.answer("✅ Admin successfully demoted!")

        admin_name = html.escape(query.from_user.first_name)
        await query.message.edit_text(
            f"<blockquote>🔻 <b>Demoted!</b>\n"
            f"✦ ━━━━━━━━━━━━━━━━━━ ✦\n"
            f"✨ <i>Admin rights removed by <a href='tg://user?id={query.from_user.id}'>{admin_name}</a>!</i></blockquote>",
            parse_mode=ParseMode.HTML,
        )
    except Exception as e:
        await query.answer(f"Error: {e}", show_alert=True)
        
