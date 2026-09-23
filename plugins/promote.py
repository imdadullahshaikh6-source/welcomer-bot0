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

# In-memory session store for pending promotions
PROMOTE_SESSIONS = {}

# Rights layout across 3 pages
RIGHTS_CONFIG = {
    1: [
        ("can_change_info", "Change Info"),
        ("can_delete_messages", "Delete Msgs"),
        ("can_invite_users", "Invite Users"),
        ("can_restrict_members", "Ban Users"),
    ],
    2: [
        ("can_pin_messages", "Pin Msgs"),
        ("can_manage_video_chats", "Manage Video"),
        ("can_promote_members", "Add Admins"),
        ("can_manage_topics", "Manage Topics"),
    ],
    3: [
        ("can_post_stories", "Post Stories"),
        ("can_edit_stories", "Edit Stories"),
        ("can_delete_stories", "Delete Stories"),
    ]
}

# Safe Default rights
DEFAULT_RIGHTS = {
    "can_change_info": False,
    "can_delete_messages": True,
    "can_invite_users": True,
    "can_restrict_members": True,
    "can_pin_messages": True,
    "can_manage_video_chats": True,
    "can_promote_members": False,
    "can_manage_topics": False,
    "can_post_stories": False,
    "can_edit_stories": False,
    "can_delete_stories": False,
}

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

def build_promote_panel(chat_id: int, target_id: int, page: int = 1):
    session_key = (chat_id, target_id)
    rights = PROMOTE_SESSIONS.get(session_key, {}).get("rights", DEFAULT_RIGHTS.copy())
    
    keyboard = []
    page_rights = RIGHTS_CONFIG.get(page, [])

    row = []
    for perm_key, label in page_rights:
        is_on = rights.get(perm_key, False)
        status_icon = "🟢" if is_on else "🔴"
        btn_text = f"{status_icon} {label}"
        cb_data = f"prt_{target_id}_{page}_{perm_key[:12]}"
        row.append(InlineKeyboardButton(btn_text, callback_data=cb_data))
        if len(row) == 2:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)

    # Navigation buttons
    nav_row = []
    if page > 1:
        nav_row.append(InlineKeyboardButton("⬅️ Previous", callback_data=f"prp_{target_id}_{page - 1}"))
    if page < 3:
        nav_row.append(InlineKeyboardButton("Next ➡️", callback_data=f"prp_{target_id}_{page + 1}"))
    if nav_row:
        keyboard.append(nav_row)

    # Confirm & Cancel
    action_row = [
        InlineKeyboardButton("✅ Confirm", callback_data=f"prc_{target_id}"),
        InlineKeyboardButton("❌ Cancel", callback_data=f"prx_{target_id}")
    ]
    keyboard.append(action_row)

    return InlineKeyboardMarkup(keyboard)

# ==================== PROMOTE TRIGGER ====================
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
            "<blockquote>❓ <b>Usage:</b> Reply to user or <code>/promote @user [title]</code></blockquote>",
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

    session_key = (message.chat.id, target.id)
    PROMOTE_SESSIONS[session_key] = {
        "admin_id": message.from_user.id,
        "rights": DEFAULT_RIGHTS.copy(),
        "title": custom_title[:16],
        "target_name": getattr(target, "first_name", "User")
    }

    target_mention = get_user_mention(target)
    panel_markup = build_promote_panel(message.chat.id, target.id, page=1)

    await message.reply_text(
        f"<blockquote>⚡ <b>SELECT ADMIN RIGHTS FOR {target_mention}</b>\n"
        f"📄 <b>Page: 1/3</b>\n\n"
        f"<i>Tap permissions to enable/disable, then click Confirm!</i></blockquote>",
        reply_markup=panel_markup,
        parse_mode=ParseMode.HTML,
    )

# ==================== TOGGLE BUTTONS ====================
@Client.on_callback_query(filters.regex(r"^prt_(\d+)_(\d+)_(.+)$"))
async def promote_toggle_callback(client: Client, query: CallbackQuery):
    target_id = int(query.matches[0].group(1))
    page = int(query.matches[0].group(2))
    short_perm = query.matches[0].group(3)
    chat_id = query.message.chat.id
    session_key = (chat_id, target_id)

    session = PROMOTE_SESSIONS.get(session_key)
    if not session:
        return await query.answer("⚠️ Session expired. Please run /promote again!", show_alert=True)

    if query.from_user.id != session["admin_id"]:
        return await query.answer("❌ Sirf command dene wala admin hi buttons switch kar sakta hai!", show_alert=True)

    for k in session["rights"].keys():
        if k.startswith(short_perm):
            session["rights"][k] = not session["rights"][k]
            break

    target_name = html.escape(session.get("target_name", "User"))
    panel_markup = build_promote_panel(chat_id, target_id, page=page)
    await query.message.edit_text(
        f"<blockquote>⚡ <b>SELECT ADMIN RIGHTS FOR <a href='tg://user?id={target_id}'>{target_name}</a></b>\n"
        f"📄 <b>Page: {page}/3</b>\n\n"
        f"<i>Tap permissions to enable/disable, then click Confirm!</i></blockquote>",
        reply_markup=panel_markup,
        parse_mode=ParseMode.HTML,
    )
    await query.answer()

# ==================== PAGE NAVIGATION ====================
@Client.on_callback_query(filters.regex(r"^prp_(\d+)_(\d+)$"))
async def promote_page_callback(client: Client, query: CallbackQuery):
    target_id = int(query.matches[0].group(1))
    new_page = int(query.matches[0].group(2))
    chat_id = query.message.chat.id
    session_key = (chat_id, target_id)

    session = PROMOTE_SESSIONS.get(session_key)
    if not session:
        return await query.answer("⚠️ Session expired. Please run /promote again!", show_alert=True)

    if query.from_user.id != session["admin_id"]:
        return await query.answer("❌ Sirf command dene wala admin hi page badal sakta hai!", show_alert=True)

    target_name = html.escape(session.get("target_name", "User"))
    panel_markup = build_promote_panel(chat_id, target_id, page=new_page)
    await query.message.edit_text(
        f"<blockquote>⚡ <b>SELECT ADMIN RIGHTS FOR <a href='tg://user?id={target_id}'>{target_name}</a></b>\n"
        f"📄 <b>Page: {new_page}/3</b>\n\n"
        f"<i>Tap permissions to enable/disable, then click Confirm!</i></blockquote>",
        reply_markup=panel_markup,
        parse_mode=ParseMode.HTML,
    )
    await query.answer()

# ==================== CONFIRM ====================
@Client.on_callback_query(filters.regex(r"^prc_(\d+)$"))
async def promote_confirm_callback(client: Client, query: CallbackQuery):
    target_id = int(query.matches[0].group(1))
    chat_id = query.message.chat.id
    session_key = (chat_id, target_id)

    session = PROMOTE_SESSIONS.get(session_key)
    if not session:
        return await query.answer("⚠️ Session expired! Please re-run .promote", show_alert=True)

    if query.from_user.id != session["admin_id"]:
        return await query.answer("❌ Sirf command dene wala admin hi Confirm kar sakta hai!", show_alert=True)

    r = session["rights"]
    custom_title = session.get("title", "Admin")

    try:
        bot_member = await client.get_chat_member(chat_id, "me")
        if bot_member.status != ChatMemberStatus.ADMINISTRATOR and bot_member.status != ChatMemberStatus.OWNER:
            return await query.answer("❌ Bot group me admin nahi hai!", show_alert=True)
    except Exception as e:
        return await query.answer(f"Bot check error: {e}", show_alert=True)

    privs = ChatPrivileges(
        can_manage_chat=True,
        can_change_info=r.get("can_change_info", False),
        can_delete_messages=r.get("can_delete_messages", False),
        can_invite_users=r.get("can_invite_users", False),
        can_restrict_members=r.get("can_restrict_members", False),
        can_pin_messages=r.get("can_pin_messages", False),
        can_manage_video_chats=r.get("can_manage_video_chats", False),
        can_promote_members=r.get("can_promote_members", False),
    )

    try:
        await client.promote_chat_member(chat_id, target_id, privs)
    except RPCError as tg_err:
        return await query.answer(f"❌ Telegram Error:\n{tg_err.MESSAGE}", show_alert=True)
    except Exception as general_err:
        return await query.answer(f"❌ Error: {str(general_err)}", show_alert=True)

    try:
        await client.set_administrator_title(chat_id, target_id, custom_title[:16])
    except Exception:
        pass

    target_name = html.escape(session.get("target_name", "User"))
    admin_name = html.escape(query.from_user.first_name)
    PROMOTE_SESSIONS.pop(session_key, None)

    await query.message.edit_text(
        f"<blockquote>🎖️ <b>Promoted Successfully!</b>\n"
        f"✦ ━━━━━━━━━━━━━━━━━━ ✦\n"
        f"👤 <b>Admin:</b> <a href='tg://user?id={target_id}'>{target_name}</a>\n"
        f"🏷️ <b>Title:</b> <code>{html.escape(custom_title)}</code>\n"
        f"👮‍♂️ <b>Promoted By:</b> <a href='tg://user?id={query.from_user.id}'>{admin_name}</a>\n"
        f"✨ <i>Permissions applied and verified!</i></blockquote>",
        parse_mode=ParseMode.HTML,
    )
    await query.answer("✅ Promoted with selected rights!")

# ==================== CANCEL ====================
@Client.on_callback_query(filters.regex(r"^prx_(\d+)$"))
async def promote_cancel_callback(client: Client, query: CallbackQuery):
    target_id = int(query.matches[0].group(1))
    chat_id = query.message.chat.id
    session_key = (chat_id, target_id)

    session = PROMOTE_SESSIONS.get(session_key)
    if session and query.from_user.id != session["admin_id"]:
        return await query.answer("❌ Sirf command dene wala admin hi cancel kar sakta hai!", show_alert=True)

    PROMOTE_SESSIONS.pop(session_key, None)
    await query.message.edit_text("<blockquote>❌ <b>Promotion cancelled!</b></blockquote>", parse_mode=ParseMode.HTML)
    await query.answer("Cancelled")

# ==================== DEMOTE (DIRECT REVOKE) ====================
@Client.on_message(filters.command(["demote"], prefixes=[".", "/"]) & filters.group)
async def demote_direct_command(client: Client, message: Message):
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
            "<blockquote>⚠️ <b>User par reply karein ya tag karein:</b>\n<code>.demote @username</code></blockquote>",
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
        target_mention = get_user_mention(target)
        admin_mention = get_user_mention(message.from_user)

        await message.reply_text(
            f"<blockquote>🔻 <b>Demoted!</b>\n"
            f"✦ ━━━━━━━━━━━━━━━━━━ ✦\n"
            f"👤 <b>User:</b> {target_mention}\n"
            f"👮‍♂️ <b>Demoted By:</b> {admin_mention}\n"
            f"✨ <i>All admin privileges revoked!</i></blockquote>",
            parse_mode=ParseMode.HTML,
        )
    except Exception as e:
        await message.reply_text(
            f"<blockquote>⚠️ <b>Failed to demote:</b> <code>{html.escape(str(e))}</code></blockquote>",
            parse_mode=ParseMode.HTML,
    )
        
