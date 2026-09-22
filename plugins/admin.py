import html
from pyrogram import Client, filters
from pyrogram.enums import ParseMode, ChatMemberStatus, MessageEntityType
from pyrogram.types import (
    Message,
    CallbackQuery,
    ChatPermissions,
    ChatPrivileges,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

warn_data = {}


async def get_admin_privileges(client: Client, user_id: int, chat_id: int):
    try:
        member = await client.get_chat_member(chat_id, user_id)
        if member.status == ChatMemberStatus.OWNER:
            return True, "owner"
        elif member.status == ChatMemberStatus.ADMINISTRATOR:
            return True, member.privileges
        return False, None
    except Exception:
        return False, None


async def extract_target_user(client: Client, message: Message):
    if message.reply_to_message:
        if message.reply_to_message.from_user:
            return message.reply_to_message.from_user
        elif message.reply_to_message.sender_chat:
            return message.reply_to_message.sender_chat

    if message.entities:
        for ent in message.entities:
            if ent.type == MessageEntityType.TEXT_MENTION and ent.user:
                return ent.user
            elif ent.type == MessageEntityType.MENTION:
                raw_user = message.text[ent.offset : ent.offset + ent.length]
                try:
                    return await client.get_users(raw_user)
                except Exception:
                    pass

    parts = message.text.split(maxsplit=2)
    if len(parts) > 1:
        arg = parts[1].strip()
        try:
            if arg.isdigit() or arg.startswith("-100"):
                return await client.get_users(int(arg))
            elif arg.startswith("@"):
                return await client.get_users(arg)
            else:
                return await client.get_users(arg)
        except Exception:
            return None

    return None


def get_user_mention(user):
    if hasattr(user, "first_name"):
        name = html.escape(user.first_name or "User")
        return f"<a href='tg://user?id={user.id}'>{name}</a>"
    elif hasattr(user, "title"):
        return f"<b>{html.escape(user.title)}</b>"
    return "User"


@Client.on_message(filters.command(["ban"], prefixes=[".", "/"]) & filters.group)
async def ban_command(client: Client, message: Message):
    if not message.from_user:
        return

    is_adm, privs = await get_admin_privileges(client, message.from_user.id, message.chat.id)
    if not is_adm:
        return

    if privs != "owner" and not (privs and privs.can_restrict_members):
        return await message.reply_text(
            "<blockquote>❌ <b>Permission Denied!</b>\nAapke paas members ko restrict/ban karne ka right nahi hai.</blockquote>",
            parse_mode=ParseMode.HTML,
        )

    target = await extract_target_user(client, message)
    if not target:
        return await message.reply_text(
            "<blockquote>⚠️ <b>User par reply karein ya tag karein:</b> <code>.ban @username</code></blockquote>",
            parse_mode=ParseMode.HTML,
        )

    bot = await client.get_me()
    if target.id == bot.id:
        return await message.reply_text(
            "<blockquote>🥺 Main khud ko ban nahi kar sakti!</blockquote>",
            parse_mode=ParseMode.HTML,
        )

    target_is_adm, _ = await get_admin_privileges(client, target.id, message.chat.id)
    if target_is_adm:
        return await message.reply_text(
            "<blockquote>❌ <b>Admin ko ban nahi kiya ja sakta!</b></blockquote>",
            parse_mode=ParseMode.HTML,
        )

    try:
        await client.ban_chat_member(message.chat.id, target.id)
        mention = get_user_mention(target)
        btn = InlineKeyboardMarkup(
            [[InlineKeyboardButton("✨ Unban Member", callback_data=f"adm_unban_{target.id}")]]
        )
        await message.reply_text(
            f"<blockquote>🚫 <b>Banned!</b>\n👤 <b>User:</b> {mention}\n⚡ <b>Action:</b> Successfully removed from group.</blockquote>",
            reply_markup=btn,
            parse_mode=ParseMode.HTML,
        )
    except Exception as e:
        await message.reply_text(
            f"<blockquote>⚠️ <b>Failed to ban:</b> <code>{html.escape(str(e))}</code></blockquote>",
            parse_mode=ParseMode.HTML,
        )


@Client.on_message(filters.command(["unban"], prefixes=[".", "/"]) & filters.group)
async def unban_command(client: Client, message: Message):
    if not message.from_user:
        return

    is_adm, privs = await get_admin_privileges(client, message.from_user.id, message.chat.id)
    if not is_adm:
        return

    if privs != "owner" and not (privs and privs.can_restrict_members):
        return await message.reply_text(
            "<blockquote>❌ <b>Permission Denied!</b>\nAapke paas members ko unban karne ka right nahi hai.</blockquote>",
            parse_mode=ParseMode.HTML,
        )

    target = await extract_target_user(client, message)
    if not target:
        return await message.reply_text(
            "<blockquote>⚠️ <b>User par reply karein ya tag karein:</b> <code>.unban @username</code></blockquote>",
            parse_mode=ParseMode.HTML,
        )

    try:
        await client.unban_chat_member(message.chat.id, target.id)
        mention = get_user_mention(target)
        await message.reply_text(
            f"<blockquote>✅ <b>Unbanned!</b>\n👤 <b>User:</b> {mention}\n✨ <b>Status:</b> Ab yeh user group wapas join kar sakta hai.</blockquote>",
            parse_mode=ParseMode.HTML,
        )
    except Exception as e:
        await message.reply_text(
            f"<blockquote>⚠️ <b>Failed to unban:</b> <code>{html.escape(str(e))}</code></blockquote>",
            parse_mode=ParseMode.HTML,
        )


@Client.on_message(filters.command(["mute"], prefixes=[".", "/"]) & filters.group)
async def mute_command(client: Client, message: Message):
    if not message.from_user:
        return

    is_adm, privs = await get_admin_privileges(client, message.from_user.id, message.chat.id)
    if not is_adm:
        return

    if privs != "owner" and not (privs and privs.can_restrict_members):
        return await message.reply_text(
            "<blockquote>❌ <b>Permission Denied!</b>\nAapke paas members ko mute karne ka right nahi hai.</blockquote>",
            parse_mode=ParseMode.HTML,
        )

    target = await extract_target_user(client, message)
    if not target:
        return await message.reply_text(
            "<blockquote>⚠️ <b>User par reply karein ya tag karein:</b> <code>.mute @username</code></blockquote>",
            parse_mode=ParseMode.HTML,
        )

    bot = await client.get_me()
    if target.id == bot.id:
        return await message.reply_text(
            "<blockquote>🥺 Main khud ko mute nahi kar sakti!</blockquote>",
            parse_mode=ParseMode.HTML,
        )

    target_is_adm, _ = await get_admin_privileges(client, target.id, message.chat.id)
    if target_is_adm:
        return await message.reply_text(
            "<blockquote>❌ <b>Admin ko mute nahi kiya ja sakta!</b></blockquote>",
            parse_mode=ParseMode.HTML,
        )

    try:
        await client.restrict_chat_member(
            chat_id=message.chat.id,
            user_id=target.id,
            permissions=ChatPermissions(can_send_messages=False),
        )
        mention = get_user_mention(target)
        btn = InlineKeyboardMarkup(
            [[InlineKeyboardButton("🔊 Unmute Member", callback_data=f"adm_unmute_{target.id}")]]
        )
        await message.reply_text(
            f"<blockquote>🤐 <b>Muted!</b>\n👤 <b>User:</b> {mention}\n🔇 <b>Status:</b> Ab yeh message nahi bhej sakte.</blockquote>",
            reply_markup=btn,
            parse_mode=ParseMode.HTML,
        )
    except Exception as e:
        await message.reply_text(
            f"<blockquote>⚠️ <b>Failed to mute:</b> <code>{html.escape(str(e))}</code></blockquote>",
            parse_mode=ParseMode.HTML,
        )


@Client.on_message(filters.command(["unmute"], prefixes=[".", "/"]) & filters.group)
async def unmute_command(client: Client, message: Message):
    if not message.from_user:
        return

    is_adm, privs = await get_admin_privileges(client, message.from_user.id, message.chat.id)
    if not is_adm:
        return

    if privs != "owner" and not (privs and privs.can_restrict_members):
        return await message.reply_text(
            "<blockquote>❌ <b>Permission Denied!</b>\nAapke paas members ko unmute karne ka right nahi hai.</blockquote>",
            parse_mode=ParseMode.HTML,
        )

    target = await extract_target_user(client, message)
    if not target:
        return await message.reply_text(
            "<blockquote>⚠️ <b>User par reply karein ya tag karein:</b> <code>.unmute @username</code></blockquote>",
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
            f"<blockquote>🔊 <b>Unmuted!</b>\n👤 <b>User:</b> {mention}\n💬 <b>Status:</b> Restrictions removed!</blockquote>",
            parse_mode=ParseMode.HTML,
        )
    except Exception as e:
        await message.reply_text(
            f"<blockquote>⚠️ <b>Failed to unmute:</b> <code>{html.escape(str(e))}</code></blockquote>",
            parse_mode=ParseMode.HTML,
        )


@Client.on_message(filters.command(["kick"], prefixes=[".", "/"]) & filters.group)
async def kick_command(client: Client, message: Message):
    if not message.from_user:
        return

    is_adm, privs = await get_admin_privileges(client, message.from_user.id, message.chat.id)
    if not is_adm:
        return

    if privs != "owner" and not (privs and privs.can_restrict_members):
        return await message.reply_text(
            "<blockquote>❌ <b>Permission Denied!</b>\nAapke paas members ko kick karne ka right nahi hai.</blockquote>",
            parse_mode=ParseMode.HTML,
        )

    target = await extract_target_user(client, message)
    if not target:
        return await message.reply_text(
            "<blockquote>⚠️ <b>User par reply karein ya tag karein:</b> <code>.kick @username</code></blockquote>",
            parse_mode=ParseMode.HTML,
        )

    bot = await client.get_me()
    if target.id == bot.id:
        return await message.reply_text(
            "<blockquote>🥺 Main khud ko kick nahi kar sakti!</blockquote>",
            parse_mode=ParseMode.HTML,
        )

    target_is_adm, _ = await get_admin_privileges(client, target.id, message.chat.id)
    if target_is_adm:
        return await message.reply_text(
            "<blockquote>❌ <b>Admin ko kick nahi kiya ja sakta!</b></blockquote>",
            parse_mode=ParseMode.HTML,
        )

    try:
        await client.ban_chat_member(message.chat.id, target.id)
        await client.unban_chat_member(message.chat.id, target.id)
        mention = get_user_mention(target)
        await message.reply_text(
            f"<blockquote>👢 <b>Kicked!</b>\n👤 <b>User:</b> {mention}\n💨 <b>Status:</b> Group se nikal diya gaya hai.</blockquote>",
            parse_mode=ParseMode.HTML,
        )
    except Exception as e:
        await message.reply_text(
            f"<blockquote>⚠️ <b>Failed to kick:</b> <code>{html.escape(str(e))}</code></blockquote>",
            parse_mode=ParseMode.HTML,
        )


@Client.on_message(filters.command(["warn"], prefixes=[".", "/"]) & filters.group)
async def warn_command(client: Client, message: Message):
    if not message.from_user:
        return

    is_adm, privs = await get_admin_privileges(client, message.from_user.id, message.chat.id)
    if not is_adm:
        return

    if privs != "owner" and not (privs and privs.can_restrict_members):
        return await message.reply_text(
            "<blockquote>❌ <b>Permission Denied!</b>\nAapke paas members ko warn/restrict karne ka right nahi hai.</blockquote>",
            parse_mode=ParseMode.HTML,
        )

    target = await extract_target_user(client, message)
    if not target:
        return await message.reply_text(
            "<blockquote>⚠️ <b>User par reply karke warn dein:</b> <code>.warn &lt;reason&gt;</code></blockquote>",
            parse_mode=ParseMode.HTML,
        )

    bot = await client.get_me()
    if target.id == bot.id:
        return await message.reply_text(
            "<blockquote>🥺 Main khud ko warn nahi de sakti!</blockquote>",
            parse_mode=ParseMode.HTML,
        )

    target_is_adm, _ = await get_admin_privileges(client, target.id, message.chat.id)
    if target_is_adm:
        return await message.reply_text(
            "<blockquote>❌ <b>Admin ko warn nahi kiya ja sakta!</b></blockquote>",
            parse_mode=ParseMode.HTML,
        )

    parts = message.text.split(maxsplit=2)
    reason = "Rules violation"
    if message.reply_to_message and len(parts) > 1:
        reason = message.text.split(maxsplit=1)[1]
    elif len(parts) > 2:
        reason = parts[2]

    chat_id = message.chat.id
    if chat_id not in warn_data:
        warn_data[chat_id] = {}

    current_warns = warn_data[chat_id].get(target.id, 0) + 1
    warn_data[chat_id][target.id] = current_warns
    mention = get_user_mention(target)

    if current_warns >= 3:
        warn_data[chat_id][target.id] = 0
        try:
            await client.ban_chat_member(chat_id, target.id)
            btn = InlineKeyboardMarkup(
                [[InlineKeyboardButton("✨ Unban Member", callback_data=f"adm_unban_{target.id}")]]
            )
            return await message.reply_text(
                f"<blockquote>🚫 <b>3/3 Warnings Reached!</b>\n👤 <b>User:</b> {mention}\n📝 <b>Reason:</b> <i>{html.escape(reason)}</i>\n⚡ <b>Action:</b> User has been banned!</blockquote>",
                reply_markup=btn,
                parse_mode=ParseMode.HTML,
            )
        except Exception as e:
            return await message.reply_text(f"<blockquote>⚠️ Ban failed: <code>{e}</code></blockquote>")

    btn = InlineKeyboardMarkup(
        [[InlineKeyboardButton("🎀 Remove Warn (Admin Only)", callback_data=f"adm_rmwarn_{target.id}")]]
    )

    await message.reply_text(
        f"<blockquote>⚠️ <b>Warning Issued!</b>\n✦ ━━━━━━━━━━━━━━━━━━ ✦\n👤 <b>User:</b> {mention}\n📊 <b>Warnings:</b> <code>{current_warns}/3</code>; be careful!\n📝 <b>Reason:</b> <i>{html.escape(reason)}</i></blockquote>",
        reply_markup=btn,
        parse_mode=ParseMode.HTML,
    )


@Client.on_message(filters.command(["resetwarns", "rmwarn"], prefixes=[".", "/"]) & filters.group)
async def reset_warn_cmd(client: Client, message: Message):
    if not message.from_user:
        return

    is_adm, privs = await get_admin_privileges(client, message.from_user.id, message.chat.id)
    if not is_adm:
        return

    if privs != "owner" and not (privs and privs.can_restrict_members):
        return await message.reply_text(
            "<blockquote>❌ <b>Permission Denied!</b></blockquote>",
            parse_mode=ParseMode.HTML,
        )

    target = await extract_target_user(client, message)
    if not target:
        return await message.reply_text(
            "<blockquote>⚠️ User par reply karein: <code>.resetwarns</code></blockquote>",
            parse_mode=ParseMode.HTML,
        )

    chat_id = message.chat.id
    if chat_id in warn_data and target.id in warn_data[chat_id]:
        warn_data[chat_id][target.id] = 0

    mention = get_user_mention(target)
    await message.reply_text(
        f"<blockquote>✨ <b>Warnings reset for {mention}!</b> (0/3)</blockquote>",
        parse_mode=ParseMode.HTML,
    )


@Client.on_callback_query(filters.regex(r"^adm_(unban|unmute|rmwarn)_(\d+)$"))
async def admin_buttons_callback(client: Client, query: CallbackQuery):
    action = query.data.split("_")[1]
    user_id = int(query.data.split("_")[2])
    chat_id = query.message.chat.id

    is_adm, privs = await get_admin_privileges(client, query.from_user.id, chat_id)
    if not is_adm:
        return await query.answer("❌ Sirf Admins hi yeh button use kar sakte hain!", show_alert=True)

    if privs != "owner" and not (privs and privs.can_restrict_members):
        return await query.answer(
            "❌ Aapke paas members ko restrict/unrestrict karne ka right nahi hai!",
            show_alert=True,
        )

    try:
        if action == "unban":
            await client.unban_chat_member(chat_id, user_id)
            await query.answer("✅ User unbanned!")
            await query.message.edit_text(
                f"<blockquote>✨ <b>User unbanned by <a href='tg://user?id={query.from_user.id}'>{html.escape(query.from_user.first_name)}</a>!</b></blockquote>",
                parse_mode=ParseMode.HTML,
            )
        elif action == "unmute":
            chat = await client.get_chat(chat_id)
            default_perms = chat.permissions or ChatPermissions(
                can_send_messages=True, can_send_media_messages=True
            )
            await client.restrict_chat_member(chat_id, user_id, default_perms)
            await query.answer("🔊 User unmuted!")
            await query.message.edit_text(
                f"<blockquote>🔊 <b>User unmuted by <a href='tg://user?id={query.from_user.id}'>{html.escape(query.from_user.first_name)}</a>!</b></blockquote>",
                parse_mode=ParseMode.HTML,
            )
        elif action == "rmwarn":
            if chat_id in warn_data and user_id in warn_data[chat_id]:
                warn_data[chat_id][user_id] = max(0, warn_data[chat_id][user_id] - 1)
                rem = warn_data[chat_id][user_id]
                await query.answer(f"Warn removed! Ab {rem}/3 bache hain.")
                await query.message.edit_text(
                    f"<blockquote>🎀 <b>Warn removed by <a href='tg://user?id={query.from_user.id}'>{html.escape(query.from_user.first_name)}</a>!</b>\nCurrent status: <code>{rem}/3</code></blockquote>",
                    parse_mode=ParseMode.HTML,
                )
            else:
                await query.answer("Is user ke paas koi active warn nahi hai.")
    except Exception as e:
        await query.answer(f"Error: {e}", show_alert=True)


@Client.on_message(filters.command(["promote"], prefixes=[".", "/"]) & filters.group)
async def promote_command(client: Client, message: Message):
    if not message.from_user:
        return

    is_adm, privs = await get_admin_privileges(client, message.from_user.id, message.chat.id)
    if not is_adm:
        return

    if privs != "owner" and not (privs and privs.can_promote_members):
        return await message.reply_text(
            "<blockquote>❌ <b>Permission Denied!</b>\nAapke paas new admins promote karne ka right nahi hai.</blockquote>",
            parse_mode=ParseMode.HTML,
        )

    target = await extract_target_user(client, message)
    if not target:
        return await message.reply_text(
            "<blockquote>⚠️ <b>User par reply karke promote karein:</b> <code>.promote &lt;title&gt;</code></blockquote>",
            parse_mode=ParseMode.HTML,
        )

    parts = message.text.split(maxsplit=2)
    custom_title = "Admin"
    if message.reply_to_message and len(parts) > 1:
        custom_title = parts[1]
    elif len(parts) > 2:
        custom_title = parts[2]

    try:
        p_rights = ChatPrivileges(
            can_manage_chat=True,
            can_delete_messages=True,
            can_manage_video_chats=True,
            can_restrict_members=True,
            can_promote_members=False,
       
