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
from pyrogram.errors import RPCError

# In-memory sessions
PROMOTE_SESSIONS = {}

# Exact permissions list according to your settings
PERMISSIONS_MAP = [
    ("can_change_info", "Change Info"),
    ("can_delete_messages", "Delete Messages"),
    ("can_restrict_members", "Ban Users"),
    ("can_invite_users", "Add Users"),
    ("can_pin_messages", "Pin Messages"),
    ("can_manage_video_chats", "Manage Live Streams"),
    ("can_promote_members", "Add New Admins"),
    ("is_anonymous", "Remain Anonymous"),
    ("can_post_stories", "Manage Stories"),
]

# Aapke bataye gaye Default Settings
EXACT_DEFAULTS = {
    "can_change_info": False,         # Change info: OFF
    "can_delete_messages": True,      # Dlt massage: ON
    "can_restrict_members": False,    # Ban: OFF
    "can_invite_users": False,        # Add Users: OFF
    "can_pin_messages": True,         # Pin Messages: ON
    "can_manage_video_chats": True,   # Manage Live Streams: ON
    "can_promote_members": False,     # Add New Admins: OFF
    "is_anonymous": False,            # Remain Anonymous: OFF
    "can_post_stories": False,        # Manage Stories: OFF
    "can_edit_stories": False,
    "can_delete_stories": False,
}

async def check_bot_admin_rights(client: Client, chat_id: int):
    """Check karta hai ki Bot khud admin hai ya nahi"""
    try:
        me = await client.get_chat_member(chat_id, "me")
        if me.status == ChatMemberStatus.ADMINISTRATOR:
            if me.privileges and me.privileges.can_promote_members:
                return True, "ok"
            return False, "rights"
        elif me.status == ChatMemberStatus.OWNER:
            return True, "ok"
        return False, "not_admin"
    except Exception:
        return False, "not_admin"

async def check_sender_admin(client: Client, message: Message):
    if message.sender_chat and message.sender_chat.id == message.chat.id:
        return True
    if not message.from_user:
        return False
    try:
        m = await client.get_chat_member(message.chat.id, message.from_user.id)
        if m.status in [ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR]:
            if m.status == ChatMemberStatus.OWNER or (m.privileges and m.privileges.can_promote_members):
                return True
    except Exception:
        pass
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

def build_simple_panel(chat_id: int, target_id: int, expanded: bool = False):
    session_key = (chat_id, target_id)
    session = PROMOTE_SESSIONS.get(session_key, {})
    rights = session.get("rights", EXACT_DEFAULTS.copy())

    keyboard = []

    if expanded:
        # Jab admin ne 'Change Permissions' choose kiya
        row = []
        for perm_key, label in PERMISSIONS_MAP:
            is_on = rights.get(perm_key, False)
            icon = "🟢" if is_on else "🔴"
            row.append(InlineKeyboardButton(f"{icon} {label}", callback_data=f"tgl_{target_id}_{perm_key[:10]}"))
            if len(row) == 2:
                keyboard.append(row)
                row = []
        if row:
            keyboard.append(row)

        keyboard.append([
            InlineKeyboardButton("✅ Confirm & Promote", callback_data=f"pconf_{target_id}"),
            InlineKeyboardButton("❌ Cancel", callback_data=f"pcanc_{target_id}")
        ])
    else:
        # Shuru me sirf 2 main buttons
        keyboard.append([
            InlineKeyboardButton("⚙️ Change Permissions", callback_data=f"pexp_{target_id}"),
            InlineKeyboardButton("✅ Confirm", callback_data=f"pconf_{target_id}")
        ])
        keyboard.append([InlineKeyboardButton("❌ Cancel", callback_data=f"pcanc_{target_id}")])

    return InlineKeyboardMarkup(keyboard)

# ==================== PROMOTE TRIGGER ====================
@Client.on_message(filters.command(["promote"], prefixes=[".", "/"]) & filters.group)
async def promote_command(client: Client, message: Message):
    # 1. BOT ADMIN CHECK (Glitch Fix)
    bot_ok, reason = await check_bot_admin_rights(client, message.chat.id)
    if not bot_ok:
        if reason == "rights":
            return await message.reply_text(
                "<blockquote>⚠️ <b>Give me admin with 'Add New Admins' right to do this!</b></blockquote>",
                parse_mode=ParseMode.HTML
            )
        return await message.reply_text(
            "<blockquote>⚠️ <b>Give me admin to do this!</b></blockquote>",
            parse_mode=ParseMode.HTML
        )

    # 2. SENDER ADMIN CHECK
    is_admin = await check_sender_admin(client, message)
    if not is_admin:
        return await message.reply_text(
            "<blockquote>❌ <b>Permission Denied!</b>\nSirf Admins hi kisi ko promote kar sakte hain.</blockquote>",
            parse_mode=ParseMode.HTML
        )

    # 3. TARGET USER CHECK
    target = await extract_target_user(client, message)
    if not target:
        return await message.reply_text(
            "<blockquote>❓ <b>Usage:</b> Reply to user or <code>.promote @username [title]</code></blockquote>",
            parse_mode=ParseMode.HTML
        )

    bot = await client.get_me()
    if target.id == bot.id:
        return await message.reply_text("<blockquote>🥺 Main pehle se is group me hoon!</blockquote>", parse_mode=ParseMode.HTML)

    parts = message.text.split(maxsplit=2)
    custom_title = "Admin"
    if message.reply_to_message and len(parts) > 1:
        custom_title = message.text.split(maxsplit=1)[1]
    elif not message.reply_to_message and len(parts) > 2:
        custom_title = parts[2]

    sender_id = message.from_user.id if message.from_user else message.chat.id
    target_name = getattr(target, "first_name", getattr(target, "title", "User"))
    session_key = (message.chat.id, target.id)

    PROMOTE_SESSIONS[session_key] = {
        "admin_id": sender_id,
        "rights": EXACT_DEFAULTS.copy(),
        "title": custom_title[:16],
        "target_name": target_name,
        "expanded": False
    }

    markup = build_simple_panel(message.chat.id, target.id, expanded=False)
    target_mention = get_user_mention(target)

    await message.reply_text(
        f"<blockquote>⚡ <b>Promote Admin:</b> {target_mention}\n"
        f"🏷️ <b>Title:</b> <code>{html.escape(custom_title[:16])}</code>\n\n"
        f"<i>Confirm dabayein default permissions ke sath promote karne ke liye, ya Permissions badle!</i></blockquote>",
        reply_markup=markup,
        parse_mode=ParseMode.HTML
    )

# ==================== CHANGE PERMISSIONS BUTTON ====================
@Client.on_callback_query(filters.regex(r"^pexp_(\d+)$"))
async def promote_expand_callback(client: Client, query: CallbackQuery):
    target_id = int(query.matches[0].group(1))
    chat_id = query.message.chat.id
    session_key = (chat_id, target_id)

    session = PROMOTE_SESSIONS.get(session_key)
    if not session:
        return await query.answer("⚠️ Session expired! Dubara .promote likhein.", show_alert=True)

    if query.from_user.id != session["admin_id"]:
        return await query.answer("❌ Sirf command dene wala admin hi options badal sakta hai!", show_alert=True)

    session["expanded"] = True
    markup = build_simple_panel(chat_id, target_id, expanded=True)
    t_name = html.escape(session["target_name"])

    await query.message.edit_text(
        f"<blockquote>⚙️ <b>Custom Rights for {t_name}</b>\n\n"
        f"<i>Permissions select karein aur Confirm dabayein:</i></blockquote>",
        reply_markup=markup,
        parse_mode=ParseMode.HTML
    )
    await query.answer()

# ==================== TOGGLE PERMISSION BUTTONS ====================
@Client.on_callback_query(filters.regex(r"^tgl_(\d+)_(.+)$"))
async def promote_toggle_callback(client: Client, query: CallbackQuery):
    target_id = int(query.matches[0].group(1))
    short_key = query.matches[0].group(2)
    chat_id = query.message.chat.id
    session_key = (chat_id, target_id)

    session = PROMOTE_SESSIONS.get(session_key)
    if not session:
        return await query.answer("⚠️ Session expired!", show_alert=True)

    if query.from_user.id != session["admin_id"]:
        return await query.answer("❌ Sirf command dene wala admin hi permissions switch kar sakta hai!", show_alert=True)

    for k in session["rights"].keys():
        if k.startswith(short_key):
            session["rights"][k] = not session["rights"][k]
            # Agar stories on/off hui toh edit aur delete bhi sync karein
            if "stories" in k:
                session["rights"]["can_edit_stories"] = session["rights"][k]
                session["rights"]["can_delete_stories"] = session["rights"][k]
            break

    markup = build_simple_panel(chat_id, target_id, expanded=True)
    await query.message.edit_reply_markup(reply_markup=markup)
    await query.answer()

# ==================== CONFIRM BUTTON ====================
@Client.on_callback_query(filters.regex(r"^pconf_(\d+)$"))
async def promote_confirm_callback(client: Client, query: CallbackQuery):
    target_id = int(query.matches[0].group(1))
    chat_id = query.message.chat.id
    session_key = (chat_id, target_id)

    session = PROMOTE_SESSIONS.get(session_key)
    if not session:
        return await query.answer("⚠️ Session expired! Please re-run .promote", show_alert=True)

    if query.from_user.id != session["admin_id"]:
        return await query.answer("❌ Sirf command dene wala admin hi Confirm kar sakta hai!", show_alert=True)

    # Re-check bot rights
    bot_ok, _ = await check_bot_admin_rights(client, chat_id)
    if not bot_ok:
        return await query.answer("❌ Give me admin to do this!", show_alert=True)

    r = session["rights"]
    custom_title = session.get("title", "Admin")

    # Safe privileges object according to Pyrogram
    privs = ChatPrivileges(
        can_manage_chat=True,
        can_change_info=r.get("can_change_info", False),
        can_delete_messages=r.get("can_delete_messages", True),
        can_invite_users=r.get("can_invite_users", False),
        can_restrict_members=r.get("can_restrict_members", False),
        can_pin_messages=r.get("can_pin_messages", True),
        can_manage_video_chats=r.get("can_manage_video_chats", True),
        can_promote_members=r.get("can_promote_members", False),
        is_anonymous=r.get("is_anonymous", False),
    )

    try:
        await client.promote_chat_member(chat_id, target_id, privs)
    except RPCError as e:
        return await query.answer(f"Telegram Error:\n{e.MESSAGE}", show_alert=True)
    except Exception as e:
        return await query.answer(f"Error: {e}", show_alert=True)

    try:
        # Edit Member Tags / Title set karna
        await client.set_administrator_title(chat_id, target_id, custom_title[:16])
    except Exception:
        pass

    target_name = html.escape(session["target_name"])
    admin_name = html.escape(query.from_user.first_name)
    PROMOTE_SESSIONS.pop(session_key, None)

    await query.message.edit_text(
        f"<blockquote>🎖️ <b>Promoted Successfully!</b>\n"
        f"✦ ━━━━━━━━━━━━━━━━━━ ✦\n"
        f"👤 <b>Admin:</b> <a href='tg://user?id={target_id}'>{target_name}</a>\n"
        f"🏷️ <b>Title:</b> <code>{html.escape(custom_title)}</code>\n"
        f"👮‍♂️ <b>Promoted By:</b> <a href='tg://user?id={query.from_user.id}'>{admin_name}</a>\n"
        f"✨ <i>Permissions successfully applied!</i></blockquote>",
        parse_mode=ParseMode.HTML
    )
    await query.answer("✅ Successfully Promoted!")

# ==================== CANCEL BUTTON ====================
@Client.on_callback_query(filters.regex(r"^pcanc_(\d+)$"))
async def promote_cancel_callback(client: Client, query: CallbackQuery):
    target_id = int(query.matches[0].group(1))
    chat_id = query.message.chat.id
    session_key = (chat_id, target_id)

    session = PROMOTE_SESSIONS.get(session_key)
    if session and query.from_user.id != session["admin_id"]:
        return await query.answer("❌ Sirf command dene wala admin hi cancel kar sakta hai!", show_alert=True)

    PROMOTE_SESSIONS.pop(session_key, None)
    await query.message.edit_text("<blockquote>❌ <b>Promotion Cancelled!</b></blockquote>", parse_mode=ParseMode.HTML)
    await query.answer("Cancelled")

# ==================== DEMOTE (DIRECT REVOKE) ====================
@Client.on_message(filters.command(["demote"], prefixes=[".", "/"]) & filters.group)
async def demote_direct_command(client: Client, message: Message):
    bot_ok, _ = await check_bot_admin_rights(client, message.chat.id)
    if not bot_ok:
        return await message.reply_text(
            "<blockquote>⚠️ <b>Give me admin to do this!</b></blockquote>",
            parse_mode=ParseMode.HTML
        )

    is_admin = await check_sender_admin(client, message)
    if not is_admin:
        return await message.reply_text("<blockquote>❌ Sirf Admins hi demote kar sakte hain!</blockquote>", parse_mode=ParseMode.HTML)

    target = await extract_target_user(client, message)
    if not target:
        return await message.reply_text("<blockquote>⚠️ <b>Format:</b> <code>.demote @username</code> ya message par reply karein.</blockquote>", parse_mode=ParseMode.HTML)

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
        target_name = html.escape(getattr(target, "first_name", getattr(target, "title", "User")))
        admin_name = html.escape(message.from_user.first_name if message.from_user else "Admin")

        await message.reply_text(
            f"<blockquote>🔻 <b>Demoted!</b>\n"
            f"✦ ━━━━━━━━━━━━━━━━━━ ✦\n"
            f"👤 <b>User:</b> <a href='tg://user?id={target.id}'>{target_name}</a>\n"
            f"👮‍♂️ <b>Demoted By:</b> {admin_name}\n"
            f"✨ <i>All admin privileges revoked!</i></blockquote>",
            parse_mode=ParseMode.HTML
        )
    except Exception as e:
        await message.reply_text(f"<blockquote>⚠️ <b>Failed to demote:</b> <code>{html.escape(str(e))}</code></blockquote>", parse_mode=ParseMode.HTML)
        
