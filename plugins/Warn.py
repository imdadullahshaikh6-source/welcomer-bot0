import html
from pyrogram import Client, filters
from pyrogram.enums import ParseMode, ChatMemberStatus, MessageEntityType
from pyrogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

# In-memory storage: {chat_id: {user_id: count}}
warn_data = {}

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

# ==================== WARN ====================
@Client.on_message(filters.command(["warn"], prefixes=[".", "/"]) & filters.group)
async def warn_command(client: Client, message: Message):
    if not message.from_user:
        return

    is_adm, privs = await get_admin_privileges(client, message.from_user.id, message.chat.id)
    if not is_adm:
        return

    # Check Ban / Restrict Permission
    if privs != "owner" and not (privs and privs.can_restrict_members):
        return await message.reply_text(
            "<blockquote>❌ <b>Permission Denied!</b>\n"
            "Aapke paas members ko warn/restrict karne ka right (Ban Users) nahi hai!</blockquote>",
            parse_mode=ParseMode.HTML,
        )

    target = await extract_target_user(client, message)
    if not target:
        return await message.reply_text(
            "<blockquote>⚠️ <b>User par reply karein ya tag karein:</b>\n<code>.warn &lt;reason&gt;</code></blockquote>",
            parse_mode=ParseMode.HTML,
        )

    bot = await client.get_me()
    if target.id == bot.id:
        return await message.reply_text("<blockquote>🥺 Main khud ko warn nahi de sakti!</blockquote>", parse_mode=ParseMode.HTML)

    target_is_adm, _ = await get_admin_privileges(client, target.id, message.chat.id)
    if target_is_adm:
        return await message.reply_text("<blockquote>❌ <b>Admin ko warn nahi kiya ja sakta!</b></blockquote>", parse_mode=ParseMode.HTML)

    parts = message.text.split(maxsplit=2)
    reason = "Rules violation"
    if message.reply_to_message:
        if len(parts) > 1:
            reason = message.text.split(maxsplit=1)[1]
    else:
        if len(parts) > 2:
            reason = parts[2]

    chat_id = message.chat.id
    if chat_id not in warn_data:
        warn_data[chat_id] = {}

    current_warns = warn_data[chat_id].get(target.id, 0) + 1
    warn_data[chat_id][target.id] = current_warns
    mention = get_user_mention(target)

    # 3 Warns = Automatic Ban
    if current_warns >= 3:
        warn_data[chat_id][target.id] = 0
        try:
            await client.ban_chat_member(chat_id, target.id)
            btn = InlineKeyboardMarkup([[InlineKeyboardButton("✨ Unban Member", callback_data=f"adm_unban_{target.id}")]])
            return await message.reply_text(
                f"<blockquote>🚫 <b>3/3 Warnings Reached!</b>\n"
                f"✦ ━━━━━━━━━━━━━━━━━━ ✦\n"
                f"👤 <b>User:</b> {mention}\n"
                f"📝 <b>Reason:</b> <i>{html.escape(reason)}</i>\n"
                f"⚡ <b>Action:</b> Limit reached! User has been banned.</blockquote>",
                reply_markup=btn,
                parse_mode=ParseMode.HTML,
            )
        except Exception as e:
            return await message.reply_text(f"<blockquote>⚠️ Ban failed: <code>{html.escape(str(e))}</code></blockquote>", parse_mode=ParseMode.HTML)

    btn = InlineKeyboardMarkup([[InlineKeyboardButton("🎀 Remove Warn (Admin Only)", callback_data=f"warn_remove_{target.id}")]])
    await message.reply_text(
        f"<blockquote>⚠️ <b>Warning Issued!</b>\n"
        f"✦ ━━━━━━━━━━━━━━━━━━ ✦\n"
        f"👤 <b>User:</b> {mention}\n"
        f"📊 <b>Warnings:</b> <code>{current_warns}/3</code>; be careful!\n"
        f"📝 <b>Reason:</b> <i>{html.escape(reason)}</i></blockquote>",
        reply_markup=btn,
        parse_mode=ParseMode.HTML,
    )

# ==================== UNWARN / RMWARN ====================
@Client.on_message(filters.command(["unwarn", "rmwarn"], prefixes=[".", "/"]) & filters.group)
async def unwarn_command(client: Client, message: Message):
    if not message.from_user:
        return

    is_adm, privs = await get_admin_privileges(client, message.from_user.id, message.chat.id)
    if not is_adm:
        return

    if privs != "owner" and not (privs and privs.can_restrict_members):
        return await message.reply_text(
            "<blockquote>❌ <b>Permission Denied!</b>\n"
            "Aapke paas warn remove karne ka right nahi hai!</blockquote>",
            parse_mode=ParseMode.HTML,
        )

    target = await extract_target_user(client, message)
    if not target:
        return await message.reply_text(
            "<blockquote>⚠️ <b>User par reply karein ya tag karein:</b>\n<code>.unwarn @username</code></blockquote>",
            parse_mode=ParseMode.HTML,
        )

    chat_id = message.chat.id
    current_warns = warn_data.get(chat_id, {}).get(target.id, 0)
    mention = get_user_mention(target)

    if current_warns <= 0:
        return await message.reply_text(f"<blockquote>ℹ️ {mention} ke paas koi active warn nahi hai!</blockquote>", parse_mode=ParseMode.HTML)

    warn_data[chat_id][target.id] = current_warns - 1
    new_warns = warn_data[chat_id][target.id]

    await message.reply_text(
        f"<blockquote>🎀 <b>Warn Removed!</b>\n"
        f"✦ ━━━━━━━━━━━━━━━━━━ ✦\n"
        f"👤 <b>User:</b> {mention}\n"
        f"📊 <b>Remaining Warnings:</b> <code>{new_warns}/3</code></blockquote>",
        parse_mode=ParseMode.HTML,
    )

# ==================== RESET WARNS ====================
@Client.on_message(filters.command(["resetwarns"], prefixes=[".", "/"]) & filters.group)
async def reset_warns_command(client: Client, message: Message):
    if not message.from_user:
        return

    is_adm, privs = await get_admin_privileges(client, message.from_user.id, message.chat.id)
    if not is_adm:
        return

    if privs != "owner" and not (privs and privs.can_restrict_members):
        return await message.reply_text("<blockquote>❌ <b>Permission Denied!</b></blockquote>", parse_mode=ParseMode.HTML)

    target = await extract_target_user(client, message)
    if not target:
        return await message.reply_text("<blockquote>⚠️ User par reply karein: <code>.resetwarns</code></blockquote>", parse_mode=ParseMode.HTML)

    chat_id = message.chat.id
    if chat_id in warn_data and target.id in warn_data[chat_id]:
        warn_data[chat_id][target.id] = 0

    mention = get_user_mention(target)
    await message.reply_text(
        f"<blockquote>✨ <b>Warnings Reset!</b>\n"
        f"✦ ━━━━━━━━━━━━━━━━━━ ✦\n"
        f"👤 <b>User:</b> {mention}\n"
        f"📊 <b>Warnings:</b> <code>0/3</code> (All cleared)</blockquote>",
        parse_mode=ParseMode.HTML,
    )

# ==================== CHECK WARNS ====================
@Client.on_message(filters.command(["warns"], prefixes=[".", "/"]) & filters.group)
async def check_warns_command(client: Client, message: Message):
    target = await extract_target_user(client, message)
    if not target:
        target = message.from_user

    chat_id = message.chat.id
    w_count = warn_data.get(chat_id, {}).get(target.id, 0)
    mention = get_user_mention(target)

    await message.reply_text(
        f"<blockquote>📊 <b>Warn Status</b>\n"
        f"✦ ━━━━━━━━━━━━━━━━━━ ✦\n"
        f"👤 <b>User:</b> {mention}\n"
        f"⚠️ <b>Total Warns:</b> <code>{w_count}/3</code></blockquote>",
        parse_mode=ParseMode.HTML,
    )

# ==================== BUTTON CALLBACK ====================
@Client.on_callback_query(filters.regex(r"^warn_remove_(\d+)$"))
async def warn_button_callback(client: Client, query: CallbackQuery):
    target_id = int(query.data.split("_")[2])
    chat_id = query.message.chat.id

    is_adm, privs = await get_admin_privileges(client, query.from_user.id, chat_id)
    if not is_adm:
        return await query.answer("❌ Sirf Admins hi warn remove kar sakte hain!", show_alert=True)

    # Check Ban / Restrict Permission on button click
    if privs != "owner" and not (privs and privs.can_restrict_members):
        return await query.answer("❌ Aapke paas members ko warn/unwarn karne ka right nahi hai!", show_alert=True)

    if chat_id in warn_data and target_id in warn_data[chat_id] and warn_data[chat_id][target_id] > 0:
        warn_data[chat_id][target_id] -= 1
        rem = warn_data[chat_id][target_id]
        await query.answer(f"Warn removed! Ab {rem}/3 bache hain.")

        admin_name = html.escape(query.from_user.first_name)
        await query.message.edit_text(
            f"<blockquote>🎀 <b>Warn removed by <a href='tg://user?id={query.from_user.id}'>{admin_name}</a>!</b>\n"
            f"✦ ━━━━━━━━━━━━━━━━━━ ✦\n"
            f"📊 <b>Remaining Warnings:</b> <code>{rem}/3</code></blockquote>",
            parse_mode=ParseMode.HTML,
        )
    else:
        await query.answer("Is user ke paas koi active warn nahi hai.", show_alert=True)
  
