import html
from pyrogram import Client, filters
from pyrogram.enums import ParseMode
from pyrogram.types import (
    Message,
    CallbackQuery,
    ChatPrivileges,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

# Active promote states: chat_id_user_id -> dict
PROMOTE_CACHE = {}

PERMS_KEYS = [
    ("can_change_info", "Change Info"),
    ("can_delete_messages", "Delete Messages"),
    ("can_restrict_members", "Ban Users"),
    ("can_invite_users", "Add Users"),
    ("can_pin_messages", "Pin Messages"),
    ("can_manage_video_chats", "Manage Live Streams"),
    ("can_promote_members", "Add New Admins"),
    ("is_anonymous", "Remain Anonymous"),
]

# Aapka set kiya hua exact default
DEFAULT_RIGHTS = {
    "can_change_info": False,
    "can_delete_messages": True,
    "can_restrict_members": False,
    "can_invite_users": False,
    "can_pin_messages": True,
    "can_manage_video_chats": True,
    "can_promote_members": False,
    "is_anonymous": False,
}

def get_buttons(target_id: int, expanded: bool = False, rights: dict = None):
    if rights is None:
        rights = DEFAULT_RIGHTS
    if not expanded:
        return InlineKeyboardMarkup([
            [
                InlineKeyboardButton("⚙️ Change Permissions", callback_data=f"p_exp_{target_id}"),
                InlineKeyboardButton("✅ Confirm", callback_data=f"p_cnf_{target_id}")
            ],
            [InlineKeyboardButton("❌ Cancel", callback_data=f"p_cls_{target_id}")]
        ])
    
    rows = []
    row = []
    for k, label in PERMS_KEYS:
        icon = "🟢" if rights.get(k, False) else "🔴"
        row.append(InlineKeyboardButton(f"{icon} {label}", callback_data=f"p_t_{target_id}_{k[:8]}"))
        if len(row) == 2:
            rows.append(row)
            row = []
    if row:
        rows.append(row)
    rows.append([
        InlineKeyboardButton("✅ Confirm", callback_data=f"p_cnf_{target_id}"),
        InlineKeyboardButton("❌ Cancel", callback_data=f"p_cls_{target_id}")
    ])
    return InlineKeyboardMarkup(rows)

@Client.on_message(filters.command(["promote"], prefixes=[".", "/"]) & filters.group)
async def promote_handler(client: Client, message: Message):
    target = None
    title = "Admin"

    if message.reply_to_message:
        target = message.reply_to_message.from_user or message.reply_to_message.sender_chat
        parts = message.text.split(maxsplit=1)
        if len(parts) > 1:
            title = parts[1]
    else:
        parts = message.text.split(maxsplit=2)
        if len(parts) > 1:
            arg = parts[1]
            try:
                target = await client.get_users(int(arg) if arg.isdigit() else arg)
            except Exception:
                target = None
        if len(parts) > 2:
            title = parts[2]

    if not target:
        return await message.reply_text("<blockquote>⚠️ User ke message par reply karke ya mention karke likhein: <code>.promote @user [title]</code></blockquote>", parse_mode=ParseMode.HTML)

    bot = await client.get_me()
    if target.id == bot.id:
        return await message.reply_text("<blockquote>🥺 Main pehle se bot admin hoon!</blockquote>", parse_mode=ParseMode.HTML)

    target_name = getattr(target, "first_name", getattr(target, "title", "User"))
    sender_id = message.from_user.id if message.from_user else message.chat.id

    key = f"{message.chat.id}_{target.id}"
    PROMOTE_CACHE[key] = {
        "admin": sender_id,
        "name": target_name,
        "title": title[:16],
        "rights": DEFAULT_RIGHTS.copy()
    }

    await message.reply_text(
        f"<blockquote>⚡ <b>Promote Member:</b> <a href='tg://user?id={target.id}'>{html.escape(target_name)}</a>\n"
        f"🏷️ <b>Title:</b> <code>{html.escape(title[:16])}</code>\n\n"
        f"<i>Confirm dabayein default rights ke sath promote karne ke liye, ya Permissions badle!</i></blockquote>",
        reply_markup=get_buttons(target.id, expanded=False),
        parse_mode=ParseMode.HTML
    )

@Client.on_callback_query(filters.regex(r"^p_(exp|t|cnf|cls)_(\d+)(?:_(.+))?$"))
async def promote_cb(client: Client, query: CallbackQuery):
    action = query.matches[0].group(1)
    target_id = int(query.matches[0].group(2))
    extra = query.matches[0].group(3)
    chat_id = query.message.chat.id
    key = f"{chat_id}_{target_id}"

    data = PROMOTE_CACHE.get(key)
    if not data:
        return await query.answer("⚠️ Session expired, .promote dubara lagayein!", show_alert=True)

    if query.from_user.id != data["admin"]:
        return await query.answer("❌ Sirf command dene wala admin use kar sakta hai!", show_alert=True)

    if action == "cls":
        PROMOTE_CACHE.pop(key, None)
        await query.message.delete()
        return

    if action == "exp":
        await query.message.edit_reply_markup(reply_markup=get_buttons(target_id, expanded=True, rights=data["rights"]))
        return await query.answer()

    if action == "t" and extra:
        for k in data["rights"]:
            if k.startswith(extra):
                data["rights"][k] = not data["rights"][k]
                break
        await query.message.edit_reply_markup(reply_markup=get_buttons(target_id, expanded=True, rights=data["rights"]))
        return await query.answer()

    if action == "cnf":
        r = data["rights"]
        privs = ChatPrivileges(
            can_manage_chat=True,
            can_change_info=r["can_change_info"],
            can_delete_messages=r["can_delete_messages"],
            can_invite_users=r["can_invite_users"],
            can_restrict_members=r["can_restrict_members"],
            can_pin_messages=r["can_pin_messages"],
            can_manage_video_chats=r["can_manage_video_chats"],
            can_promote_members=r["can_promote_members"],
            is_anonymous=r["is_anonymous"]
        )

        try:
            await client.promote_chat_member(chat_id, target_id, privs)
        except Exception:
            return await query.answer("⚠️ Pehle mujhe admin banayein aur 'Add Admins' permission dein!", show_alert=True)

        try:
            await client.set_administrator_title(chat_id, target_id, data["title"])
        except Exception:
            pass

        t_name = html.escape(data["name"])
        a_name = html.escape(query.from_user.first_name)
        PROMOTE_CACHE.pop(key, None)

        await query.message.edit_text(
            f"<blockquote>🎖️ <b>Promoted Successfully!</b>\n"
            f"✦ ━━━━━━━━━━━━━━━━━━ ✦\n"
            f"👤 <b>Admin:</b> <a href='tg://user?id={target_id}'>{t_name}</a>\n"
            f"🏷️ <b>Title:</b> <code>{html.escape(data['title'])}</code>\n"
            f"👮‍♂️ <b>Promoted By:</b> {a_name}</blockquote>",
            parse_mode=ParseMode.HTML
        )
        await query.answer("✅ Promoted!")

@Client.on_message(filters.command(["demote"], prefixes=[".", "/"]) & filters.group)
async def demote_handler(client: Client, message: Message):
    target = None
    if message.reply_to_message:
        target = message.reply_to_message.from_user or message.reply_to_message.sender_chat
    else:
        parts = message.text.split(maxsplit=1)
        if len(parts) > 1:
            arg = parts[1]
            try:
                target = await client.get_users(int(arg) if arg.isdigit() else arg)
            except Exception:
                target = None

    if not target:
        return await message.reply_text("<blockquote>⚠️ User par reply karein ya tag karein: <code>.demote @user</code></blockquote>", parse_mode=ParseMode.HTML)

    try:
        no_rights = ChatPrivileges(
            can_manage_chat=False,
            can_delete_messages=False,
            can_manage_video_chats=False,
            can_restrict_members=False,
            can_promote_members=False,
            can_change_info=False,
            can_invite_users=False,
            can_pin_messages=False
        )
        await client.promote_chat_member(message.chat.id, target.id, no_rights)
        t_name = html.escape(getattr(target, "first_name", getattr(target, "title", "User")))
        await message.reply_text(
            f"<blockquote>🔻 <b>Demoted!</b>\n"
            f"👤 <b>User:</b> <a href='tg://user?id={target.id}'>{t_name}</a>\n"
            f"✨ <i>All admin privileges revoked!</i></blockquote>",
            parse_mode=ParseMode.HTML
        )
    except Exception:
        await message.reply_text("<blockquote>⚠️ Pehle mujhe admin banayein aur 'Add Admins' permission dein!</blockquote>", parse_mode=ParseMode.HTML)
        
