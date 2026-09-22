import html
from pyrogram import Client, filters
from pyrogram.enums import ParseMode, ChatMemberStatus
from pyrogram.types import Message, ChatPermissions, ChatPrivileges

async def is_admin(client: Client, user_id: int, chat_id: int) -> bool:
    try:
        member = await client.get_chat_member(chat_id, user_id)
        return member.status in [ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR]
    except Exception:
        return False

async def can_bot_moderate(client: Client, chat_id: int) -> bool:
    try:
        bot = await client.get_me()
        member = await client.get_chat_member(chat_id, bot.id)
        return member.status == ChatMemberStatus.ADMINISTRATOR and member.privileges.can_restrict_members
    except Exception:
        return False

async def extract_target_user(client: Client, message: Message):
    if message.reply_to_message:
        if message.reply_to_message.from_user:
            return message.reply_to_message.from_user
        elif message.reply_to_message.sender_chat:
            return message.reply_to_message.sender_chat

    parts = message.text.split(maxsplit=2)
    if len(parts) > 1:
        raw_user = parts[1].strip()
        try:
            if raw_user.isdigit() or raw_user.startswith("-100"):
                user_id = int(raw_user)
            else:
                user_id = raw_user
            user_obj = await client.get_users(user_id)
            return user_obj
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

# ==================== BAN ====================
@Client.on_message(filters.command(["ban"], prefixes=[".", "/"]) & filters.group)
async def ban_command(client: Client, message: Message):
    if not message.from_user or not await is_admin(client, message.from_user.id, message.chat.id):
        return

    target = await extract_target_user(client, message)
    if not target:
        return await message.reply_text(
            "<blockquote>⚠️ <b>Kisi user ke message par reply karein ya ID/Username dein:</b> <code>.ban @username</code></blockquote>",
            parse_mode=ParseMode.HTML
        )

    bot = await client.get_me()
    if target.id == bot.id:
        return await message.reply_text("<blockquote>🥺 Main khud ko ban nahi kar sakti!</blockquote>", parse_mode=ParseMode.HTML)

    if await is_admin(client, target.id, message.chat.id):
        return await message.reply_text("<blockquote>❌ <b>Admin ko ban nahi kiya ja sakta!</b></blockquote>", parse_mode=ParseMode.HTML)

    try:
        await client.ban_chat_member(message.chat.id, target.id)
        mention = get_user_mention(target)
        await message.reply_text(
            f"<blockquote>🚫 <b>Banned!</b>\n"
            f"👤 <b>User:</b> {mention}\n"
            f"⚡ <b>Action:</b> Successfully removed & blacklisted.</blockquote>",
            parse_mode=ParseMode.HTML
        )
    except Exception as e:
        await message.reply_text(f"<blockquote>⚠️ <b>Failed to ban:</b> <code>{html.escape(str(e))}</code></blockquote>", parse_mode=ParseMode.HTML)

# ==================== UNBAN ====================
@Client.on_message(filters.command(["unban"], prefixes=[".", "/"]) & filters.group)
async def unban_command(client: Client, message: Message):
    if not message.from_user or not await is_admin(client, message.from_user.id, message.chat.id):
        return

    target = await extract_target_user(client, message)
    if not target:
        return await message.reply_text(
            "<blockquote>⚠️ <b>User par reply karein ya username/ID mention karein:</b> <code>.unban @username</code></blockquote>",
            parse_mode=ParseMode.HTML
        )

    try:
        await client.unban_chat_member(message.chat.id, target.id)
        mention = get_user_mention(target)
        await message.reply_text(
            f"<blockquote>✅ <b>Unbanned!</b>\n"
            f"👤 <b>User:</b> {mention}\n"
            f"✨ <b>Status:</b> Ab yeh user group wapas join kar sakta hai.</blockquote>",
            parse_mode=ParseMode.HTML
        )
    except Exception as e:
        await message.reply_text(f"<blockquote>⚠️ <b>Failed to unban:</b> <code>{html.escape(str(e))}</code></blockquote>", parse_mode=ParseMode.HTML)

# ==================== KICK ====================
@Client.on_message(filters.command(["kick"], prefixes=[".", "/"]) & filters.group)
async def kick_command(client: Client, message: Message):
    if not message.from_user or not await is_admin(client, message.from_user.id, message.chat.id):
        return

    target = await extract_target_user(client, message)
    if not target:
        return await message.reply_text(
            "<blockquote>⚠️ <b>Kisi user par reply karein ya ID dein:</b> <code>.kick @username</code></blockquote>",
            parse_mode=ParseMode.HTML
        )

    bot = await client.get_me()
    if target.id == bot.id:
        return await message.reply_text("<blockquote>🥺 Main khud ko kick nahi kar sakti!</blockquote>", parse_mode=ParseMode.HTML)

    if await is_admin(client, target.id, message.chat.id):
        return await message.reply_text("<blockquote>❌ <b>Admin ko kick nahi kiya ja sakta!</b></blockquote>", parse_mode=ParseMode.HTML)

    try:
        # Kick means ban then unban immediately so they can re-join if they want
        await client.ban_chat_member(message.chat.id, target.id)
        await client.unban_chat_member(message.chat.id, target.id)
        mention = get_user_mention(target)
        await message.reply_text(
            f"<blockquote>👢 <b>Kicked!</b>\n"
            f"👤 <b>User:</b> {mention}\n"
            f"💨 <b>Status:</b> Group se nikal diya gaya hai.</blockquote>",
            parse_mode=ParseMode.HTML
        )
    except Exception as e:
        await message.reply_text(f"<blockquote>⚠️ <b>Failed to kick:</b> <code>{html.escape(str(e))}</code></blockquote>", parse_mode=ParseMode.HTML)

# ==================== MUTE ====================
@Client.on_message(filters.command(["mute"], prefixes=[".", "/"]) & filters.group)
async def mute_command(client: Client, message: Message):
    if not message.from_user or not await is_admin(client, message.from_user.id, message.chat.id):
        return

    target = await extract_target_user(client, message)
    if not target:
        return await message.reply_text(
            "<blockquote>⚠️ <b>Kisi user par reply karein ya ID dein:</b> <code>.mute @username</code></blockquote>",
            parse_mode=ParseMode.HTML
        )

    bot = await client.get_me()
    if target.id == bot.id:
        return await message.reply_text("<blockquote>🥺 Main khud ko mute nahi kar sakti!</blockquote>", parse_mode=ParseMode.HTML)

    if await is_admin(client, target.id, message.chat.id):
        return await message.reply_text("<blockquote>❌ <b>Admin ko mute nahi kiya ja sakta!</b></blockquote>", parse_mode=ParseMode.HTML)

    try:
        await client.restrict_chat_member(
            chat_id=message.chat.id,
            user_id=target.id,
            permissions=ChatPermissions(can_send_messages=False)
        )
        mention = get_user_mention(target)
        await message.reply_text(
            f"<blockquote>🤐 <b>Muted!</b>\n"
            f"👤 <b>User:</b> {mention}\n"
            f"🔇 <b>Status:</b> Ab yeh message nahi bhej sakte.</blockquote>",
            parse_mode=ParseMode.HTML
        )
    except Exception as e:
        await message.reply_text(f"<blockquote>⚠️ <b>Failed to mute:</b> <code>{html.escape(str(e))}</code></blockquote>", parse_mode=ParseMode.HTML)

# ==================== UNMUTE ====================
@Client.on_message(filters.command(["unmute"], prefixes=[".", "/"]) & filters.group)
async def unmute_command(client: Client, message: Message):
    if not message.from_user or not await is_admin(client, message.from_user.id, message.chat.id):
        return

    target = await extract_target_user(client, message)
    if not target:
        return await message.reply_text(
            "<blockquote>⚠️ <b>Kisi user par reply karein ya ID dein:</b> <code>.unmute @username</code></blockquote>",
            parse_mode=ParseMode.HTML
        )

    try:
        chat = await client.get_chat(message.chat.id)
        default_perms = chat.permissions or ChatPermissions(
            can_send_messages=True,
            can_send_media_messages=True,
            can_send_other_messages=True,
            can_add_web_page_previews=True
        )
        await client.restrict_chat_member(
            chat_id=message.chat.id,
            user_id=target.id,
            permissions=default_perms
        )
        mention = get_user_mention(target)
        await message.reply_text(
            f"<blockquote>🔊 <b>Unmuted!</b>\n"
            f"👤 <b>User:</b> {mention}\n"
            f"💬 <b>Status:</b> Restrictions removed, bol sakte hain ab!</blockquote>",
            parse_mode=ParseMode.HTML
        )
    except Exception as e:
        await message.reply_text(f"<blockquote>⚠️ <b>Failed to unmute:</b> <code>{html.escape(str(e))}</code></blockquote>", parse_mode=ParseMode.HTML)

# ==================== PROMOTE ====================
@Client.on_message(filters.command(["promote"], prefixes=[".", "/"]) & filters.group)
async def promote_command(client: Client, message: Message):
    if not message.from_user or not await is_admin(client, message.from_user.id, message.chat.id):
        return

    target = await extract_target_user(client, message)
    if not target:
        return await message.reply_text(
            "<blockquote>⚠️ <b>User par reply karke promote karein:</b> <code>.promote &lt;title&gt;</code></blockquote>",
            parse_mode=ParseMode.HTML
        )

    parts = message.text.split(maxsplit=2)
    custom_title = "Admin"
    if message.reply_to_message and len(parts) > 1:
        custom_title = parts[1]
    elif len(parts) > 2:
        custom_title = parts[2]

    try:
        privs = ChatPrivileges(
            can_manage_chat=True,
            can_delete_messages=True,
            can_manage_video_chats=True,
            can_restrict_members=True,
            can_promote_members=False,
            can_change_info=True,
            can_invite_users=True,
            can_pin_messages=True
        )
        await client.promote_chat_member(message.chat.id, target.id, privs)
        try:
            await client.set_administrator_title(message.chat.id, target.id, custom_title[:16])
        except Exception:
            pass

        mention = get_user_mention(target)
        await message.reply_text(
            f"<blockquote>🎖️ <b>Promoted!</b>\n"
            f"👤 <b>User:</b> {mention}\n"
            f"🏷️ <b>Title:</b> <code>{html.escape(custom_title)}</code>\n"
            f"⚡ <b>Status:</b> Admin rights granted!</blockquote>",
            parse_mode=ParseMode.HTML
        )
    except Exception as e:
        await message.reply_text(f"<blockquote>⚠️ <b>Failed to promote:</b> <code>{html.escape(str(e))}</code></blockquote>", parse_mode=ParseMode.HTML)

# ==================== DEMOTE ====================
@Client.on_message(filters.command(["demote"], prefixes=[".", "/"]) & filters.group)
async def demote_command(client: Client, message: Message):
    if not message.from_user or not await is_admin(client, message.from_user.id, message.chat.id):
        return

    target = await extract_target_user(client, message)
    if not target:
        return await message.reply_text(
            "<blockquote>⚠️ <b>User par reply karein:</b> <code>.demote</code></blockquote>",
            parse_mode=ParseMode.HTML
        )

    try:
        no_privs = ChatPrivileges(
            can_manage_chat=False,
            can_delete_messages=False,
            can_manage_video_chats=False,
            can_restrict_members=False,
            can_promote_members=False,
            can_change_info=False,
            can_invite_users=False,
            can_pin_messages=False
        )
        await client.promote_chat_member(message.chat.id, target.id, no_privs)
        mention = get_user_mention(target)
        await message.reply_text(
            f"<blockquote>🔻 <b>Demoted!</b>\n"
            f"👤 <b>User:</b> {mention}\n"
            f"⚡ <b>Status:</b> Admin rights removed!</blockquote>",
            parse_mode=ParseMode.HTML
        )
    except Exception as e:
        await message.reply_text(f"<blockquote>⚠️ <b>Failed to demote:</b> <code>{html.escape(str(e))}</code></blockquote>", parse_mode=ParseMode.HTML)

# ==================== PIN & UNPIN ====================
@Client.on_message(filters.command(["pin"], prefixes=[".", "/"]) & filters.group)
async def pin_command(client: Client, message: Message):
    if not message.from_user or not await is_admin(client, message.from_user.id, message.chat.id):
        return

    if not message.reply_to_message:
        return await message.reply_text("<blockquote>⚠️ <b>Kisi message par reply karke <code>.pin</code> karein.</b></blockquote>", parse_mode=ParseMode.HTML)

    is_loud = "loud" in message.text.lower()
    try:
        await client.pin_chat_message(
            chat_id=message.chat.id,
            message_id=message.reply_to_message.id,
            disable_notification=not is_loud
        )
        await message.reply_text(
            f"<blockquote>📌 <b>Pinned!</b>\nNotify: <code>{'ON 🔔' if is_loud else 'OFF 🔕'}</code></blockquote>",
            parse_mode=ParseMode.HTML
        )
    except Exception as e:
        await message.reply_text(f"<blockquote>⚠️ <b>Pin failed:</b> <code>{html.escape(str(e))}</code></blockquote>", parse_mode=ParseMode.HTML)

@Client.on_message(filters.command(["unpin"], prefixes=[".", "/"]) & filters.group)
async def unpin_command(client: Client, message: Message):
    if not message.from_user or not await is_admin(client, message.from_user.id, message.chat.id):
        return

    target_id = message.reply_to_message.id if message.reply_to_message else None
    try:
        await client.unpin_chat_message(chat_id=message.chat.id, message_id=target_id)
        await message.reply_text("<blockquote>📌 <b>Message Unpinned!</b></blockquote>", parse_mode=ParseMode.HTML)
    except Exception as e:
        await message.reply_text(f"<blockquote>⚠️ <b>Unpin failed:</b> <code>{html.escape(str(e))}</code></blockquote>", parse_mode=ParseMode.HTML)

@Client.on_message(filters.command(["unpinall"], prefixes=[".", "/"]) & filters.group)
async def unpinall_command(client: Client, message: Message):
    if not message.from_user or not await is_admin(client, message.from_user.id, message.chat.id):
        return

    try:
        await client.unpin_all_chat_messages(chat_id=message.chat.id)
        await message.reply_text("<blockquote>🧹 <b>All pinned messages have been unpinned!</b></blockquote>", parse_mode=ParseMode.HTML)
    except Exception as e:
        await message.reply_text(f"<blockquote>⚠️ <b>Unpinall failed:</b> <code>{html.escape(str(e))}</code></blockquote>", parse_mode=ParseMode.HTML)
                                        
