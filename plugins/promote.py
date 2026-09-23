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

# Custom Font Converter (Duke Style Small Caps)
FONT_MAP = {
    'a': 'ᴀ', 'b': 'ʙ', 'c': 'ᴄ', 'd': 'ᴅ', 'e': 'ᴇ', 'f': 'ғ', 'g': 'ɢ',
    'h': 'ʜ', 'i': 'ɪ', 'j': 'ᴊ', 'k': 'ᴋ', 'l': 'ʟ', 'm': 'ᴍ', 'n': 'ɴ',
    'o': 'ᴏ', 'p': 'ᴘ', 'q': 'ǫ', 'r': 'ʀ', 's': 's', 't': 'ᴛ', 'u': 'ᴜ',
    'v': 'ᴠ', 'w': 'ᴡ', 'x': 'x', 'y': 'ʏ', 'z': 'ᴢ',
    'A': 'A', 'B': 'B', 'C': 'C', 'D': 'D', 'E': 'E', 'F': 'F', 'G': 'G',
    'H': 'H', 'I': 'I', 'J': 'J', 'K': 'K', 'L': 'L', 'M': 'M', 'N': 'N',
    'O': 'O', 'P': 'P', 'Q': 'Q', 'R': 'R', 'S': 'S', 'T': 'T', 'U': 'U',
    'V': 'V', 'W': 'W', 'X': 'X', 'Y': 'Y', 'Z': 'Z'
}

def to_duke_font(text: str) -> str:
    return "".join(FONT_MAP.get(c, c) for c in text)

# Session Store
PROMOTE_SESSIONS = {}

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

def build_promote_panel(chat_id: int, target_id: int, page: int = 1):
    session_key = (chat_id, target_id)
    rights = PROMOTE_SESSIONS.get(session_key, {}).get("rights", DEFAULT_RIGHTS.copy())
    
    keyboard = []
    page_rights = RIGHTS_CONFIG.get(page, [])

    row = []
    for perm_key, label in page_rights:
        is_on = rights.get(perm_key, False)
        # Duke style indicator: Selected rights highlighted without heavy emojis
        status_symbol = "✓ " if is_on else "✗ "
        btn_text = status_symbol + to_duke_font(label)
        cb_data = f"prt_{target_id}_{page}_{perm_key[:12]}"
        row.append(InlineKeyboardButton(btn_text, callback_data=cb_data))
        if len(row) == 2:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)

    # Navigation Row (Duke Gothic font)
    nav_row = []
    if page > 1:
        nav_row.append(InlineKeyboardButton(to_duke_font("Previous"), callback_data=f"prp_{target_id}_{page - 1}"))
    if page < 3:
        nav_row.append(InlineKeyboardButton(to_duke_font("Next"), callback_data=f"prp_{target_id}_{page + 1}"))
    if nav_row:
        keyboard.append(nav_row)

    # Confirm Row
    keyboard.append([
        InlineKeyboardButton(to_duke_font("Confirm"), callback_data=f"prc_{target_id}")
    ])

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
            "<blockquote>❌ <b>Permission Denied!</b></blockquote>",
            parse_mode=ParseMode.HTML,
        )

    target = await extract_target_user(client, message)
    if not target:
        header_text = to_duke_font("Usage reply or /promote @user Title. Example /promote @user Moderator.")
        return await message.reply_text(
            f"<blockquote>❔ {header_text}</blockquote>",
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
    t_name = getattr(target, "first_name", "User")
    PROMOTE_SESSIONS[session_key] = {
        "admin_id": message.from_user.id,
        "rights": DEFAULT_RIGHTS.copy(),
        "title": custom_title[:16],
        "target_name": t_name
    }

    panel_markup = build_promote_panel(message.chat.id, target.id, page=1)
    
    title_text = to_duke_font("Select Admin Rights for")
    page_text = to_duke_font("Page 1/3")

    await message.reply_text(
        f"<blockquote><b>{title_text} {html.escape(t_name)}</b>\n"
        f"<b>{page_text}</b></blockquote>",
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
        return await query.answer("⚠️ Session expired!", show_alert=True)

    if query.from_user.id != session["admin_id"]:
        return await query.answer("❌ Sirf command dene wala admin hi buttons toggle kar sakta hai!", show_alert=True)

    for k in session["rights"].keys():
        if k.startswith(short_perm):
            session["rights"][k] = not session["rights"][k]
            break

    t_name = session.get("target_name", "User")
    panel_markup = build_promote_panel(chat_id, target_id, page=page)
    
    title_text = to_duke_font("Select Admin Rights for")
    page_text = to_duke_font(f"Page {page}/3")

    await query.message.edit_text(
        f"<blockquote><b>{title_text} {html.escape(t_name)}</b>\n"
        f"<b>{page_text}</b></blockquote>",
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
        return await query.answer("⚠️ Session expired!", show_alert=True)

    if query.from_user.id != session["admin_id"]:
        return await query.answer("❌ Sirf command dene wala admin hi page badal sakta hai!", show_alert=True)

    t_name = session.get("target_name", "User")
    panel_markup = build_promote_panel(chat_id, target_id, page=new_page)
    
    title_text = to_duke_font("Select Admin Rights for")
    page_text = to_duke_font(f"Page {new_page}/3")

    await query.message.edit_text(
        f"<blockquote><b>{title_text} {html.escape(t_name)}</b>\n"
        f"<b>{page_text}</b></blockquote>",
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
        return await query.answer("⚠️ Session expired!", show_alert=True)

    if query.from_user.id != session["admin_id"]:
        return await query.answer("❌ Sirf command dene wala admin hi Confirm kar sakta hai!", show_alert=True)

    r = session["rights"]
    custom_title = session.get("title", "Admin")

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
    PROMOTE_SESSIONS.pop(session_key, None)

    await query.message.edit_text(
        f"<blockquote>👑 <b>{to_duke_font('Promoted Successfully')}</b>\n"
        f"✦ ━━━━━━━━━━━━━━━━━━ ✦\n"
        f"👤 <b>Admin:</b> <a href='tg://user?id={target_id}'>{target_name}</a>\n"
        f"🏷️ <b>Title:</b> <code>{html.escape(custom_title)}</code></blockquote>",
        parse_mode=ParseMode.HTML,
    )
    await query.answer("✅ Promoted!")

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
            "<blockquote>❌ <b>Permission Denied!</b></blockquote>",
            parse_mode=ParseMode.HTML,
        )

    target = await extract_target_user(client, message)
    if not target:
        return await message.reply_text(
            "<blockquote>⚠️ <b>Format:</b> <code>.demote @username</code></blockquote>",
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
        target_name = html.escape(getattr(target, "first_name", "User"))

        await message.reply_text(
            f"<blockquote>🔻 <b>{to_duke_font('Demoted')}</b>\n"
            f"✦ ━━━━━━━━━━━━━━━━━━ ✦\n"
            f"👤 <b>User:</b> <a href='tg://user?id={target.id}'>{target_name}</a>\n"
            f"✨ <i>All admin rights revoked!</i></blockquote>",
            parse_mode=ParseMode.HTML,
        )
    except Exception as e:
        await message.reply_text(
            f"<blockquote>⚠️ <b>Failed to demote:</b> <code>{html.escape(str(e))}</code></blockquote>",
            parse_mode=ParseMode.HTML,
        )
        
