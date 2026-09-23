import os
import html
from pyrogram import Client, filters
from pyrogram.enums import ParseMode, ChatMemberStatus, MessageEntityType
from pyrogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from motor.motor_asyncio import AsyncIOMotorClient

# MongoDB Setup
MONGO_URL = os.environ.get("MONGO_URL") or os.environ.get("DATABASE_URL")
if MONGO_URL:
    mongo_client = AsyncIOMotorClient(MONGO_URL)
    db = mongo_client.get_database("WelcomerBot")
    warns_db = db.user_warns
else:
    warns_db = None

MAX_WARNS = 3

async def check_admin_sender(client: Client, chat_id: int, user_id: int):
    try:
        m = await client.get_chat_member(chat_id, user_id)
        if m.status in [ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR]:
            return True
    except Exception:
        return True
    return False

async def extract_target(client: Client, message: Message):
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

def build_warn_buttons(target_id: int):
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("➖ -1 Warn", callback_data=f"wmod_{target_id}_dec"),
            InlineKeyboardButton("➕ +1 Warn", callback_data=f"wmod_{target_id}_inc")
        ]
    ])

# ==================== WARN COMMAND ====================
@Client.on_message(filters.command(["warn", "dwarn"], prefixes=[".", "/"]) & filters.group)
async def warn_command(client: Client, message: Message):
    try:
        me = await client.get_chat_member(message.chat.id, "me")
        if me.status not in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
            return await message.reply_text(
                "<blockquote>⚠️ Give me admin with 'Ban Users' right to do this!</blockquote>",
                parse_mode=ParseMode.HTML
            )
    except Exception:
        pass

    user_id = message.from_user.id if message.from_user else (message.sender_chat.id if message.sender_chat else 0)
    is_adm = await check_admin_sender(client, message.chat.id, user_id)
    if not is_adm:
        return await message.reply_text("<blockquote>❌ Sirf Admins hi warn de sakte hain!</blockquote>", parse_mode=ParseMode.HTML)

    target = await extract_target(client, message)
    if not target:
        return await message.reply_text(
            "<blockquote>⚠️ <b>Kisi user ke message par reply karein ya tag karein:</b>\n<code>.warn @username [reason]</code></blockquote>",
            parse_mode=ParseMode.HTML
        )

    bot = await client.get_me()
    if target.id == bot.id:
        return await message.reply_text("<blockquote>🥺 Main khud ko warn nahi kar sakti!</blockquote>", parse_mode=ParseMode.HTML)

    parts = message.text.split(maxsplit=2)
    reason = "None"
    if message.reply_to_message and len(parts) > 1:
        reason = message.text.split(maxsplit=1)[1]
    elif not message.reply_to_message and len(parts) > 2:
        reason = parts[2]

    current_warns = 0
    if warns_db is not None:
        doc = await warns_db.find_one({"chat_id": message.chat.id, "user_id": target.id})
        if doc:
            current_warns = doc.get("count", 0)

    current_warns += 1

    if message.command[0].lower() == "dwarn" and message.reply_to_message:
        try:
            await message.reply_to_message.delete()
        except Exception:
            pass

    target_mention = get_user_mention(target)
    admin_mention = get_user_mention(message.from_user) if message.from_user else "Admin"

    if current_warns >= MAX_WARNS:
        if warns_db is not None:
            await warns_db.delete_one({"chat_id": message.chat.id, "user_id": target.id})
        try:
            await client.ban_chat_member(message.chat.id, target.id)
            await message.reply_text(
                f"<blockquote>🚫 <b>Limit Reached!</b>\n"
                f"✦ ━━━━━━━━━━━━━━━━━━ ✦\n"
                f"👤 <b>User:</b> {target_mention} [<code>{target.id}</code>]\n"
                f"⚠️ <b>Warns:</b> {current_warns}/{MAX_WARNS}\n"
                f"🔨 <i>Max warnings reach hone par user ko ban kar diya gaya!</i></blockquote>",
                parse_mode=ParseMode.HTML,
            )
        except Exception as e:
            await message.reply_text(f"<blockquote>⚠️ <b>Ban Error:</b> <code>{html.escape(str(e))}</code></blockquote>", parse_mode=ParseMode.HTML)
        return

    if warns_db is not None:
        await warns_db.update_one(
            {"chat_id": message.chat.id, "user_id": target.id},
            {"$set": {"count": current_warns, "reason": reason}},
            upsert=True
        )

    await message.reply_text(
        f"<blockquote>⚠️ <b>Warning Issued!</b>\n"
        f"✦ ━━━━━━━━━━━━━━━━━━ ✦\n"
        f"👤 <b>User:</b> {target_mention} [<code>{target.id}</code>]\n"
        f"👮‍♂️ <b>Admin:</b> {admin_mention}\n"
        f"📊 <b>Warnings:</b> {current_warns}/{MAX_WARNS}\n"
        f"📝 <b>Reason:</b> <i>{html.escape(reason)}</i></blockquote>",
        reply_markup=build_warn_buttons(target.id),
        parse_mode=ParseMode.HTML,
    )

# ==================== -1 / +1 BUTTONS CALLBACK ====================
@Client.on_callback_query(filters.regex(r"^wmod_(\d+)_(dec|inc)$"))
async def warn_modify_callback(client: Client, query: CallbackQuery):
    target_id = int(query.matches[0].group(1))
    action = query.matches[0].group(2)
    chat_id = query.message.chat.id

    is_adm = await check_admin_sender(client, chat_id, query.from_user.id)
    if not is_adm:
        return await query.answer("❌ Sirf Admins hi warnings modify kar sakte hain!", show_alert=True)

    current_warns = 0
    reason = "None"
    if warns_db is not None:
        doc = await warns_db.find_one({"chat_id": chat_id, "user_id": target_id})
        if doc:
            current_warns = doc.get("count", 0)
            reason = doc.get("reason", "None")

    if action == "inc":
        current_warns += 1
    elif action == "dec":
        current_warns = max(0, current_warns - 1)

    admin_name = html.escape(query.from_user.first_name)

    # Agar 3 warns ho gaye toh BAN
    if current_warns >= MAX_WARNS:
        if warns_db is not None:
            await warns_db.delete_one({"chat_id": chat_id, "user_id": target_id})
        try:
            await client.ban_chat_member(chat_id, target_id)
            await query.message.edit_text(
                f"<blockquote>🚫 <b>Limit Reached!</b>\n"
                f"✦ ━━━━━━━━━━━━━━━━━━ ✦\n"
                f"👤 <b>Target ID:</b> <code>{target_id}</code>\n"
                f"⚠️ <b>Warns:</b> {current_warns}/{MAX_WARNS}\n"
                f"🔨 <i>Max warnings hone par <a href='tg://user?id={query.from_user.id}'>{admin_name}</a> dwara ban kiya gaya!</i></blockquote>",
                parse_mode=ParseMode.HTML
            )
            return await query.answer("🚫 User banned (Max warns)!")
        except Exception as e:
            return await query.answer(f"Ban Error: {e}", show_alert=True)

    # Agar 0 ho gaye toh DB clear
    if current_warns == 0:
        if warns_db is not None:
            await warns_db.delete_one({"chat_id": chat_id, "user_id": target_id})
        await query.message.edit_text(
            f"<blockquote>✅ <b>All Warnings Cleared!</b>\n"
            f"✦ ━━━━━━━━━━━━━━━━━━ ✦\n"
            f"👤 <b>Target ID:</b> <code>{target_id}</code>\n"
            f"✨ <i>Warnings removed by <a href='tg://user?id={query.from_user.id}'>{admin_name}</a>!</i></blockquote>",
            parse_mode=ParseMode.HTML
        )
        return await query.answer("✅ All warnings cleared!")

    # Update database
    if warns_db is not None:
        await warns_db.update_one(
            {"chat_id": chat_id, "user_id": target_id},
            {"$set": {"count": current_warns, "reason": reason}},
            upsert=True
        )

    await query.message.edit_text(
        f"<blockquote>⚠️ <b>Warning Updated!</b>\n"
        f"✦ ━━━━━━━━━━━━━━━━━━ ✦\n"
        f"👤 <b>Target ID:</b> <code>{target_id}</code>\n"
        f"👮‍♂️ <b>Updated By:</b> <a href='tg://user?id={query.from_user.id}'>{admin_name}</a>\n"
        f"📊 <b>Warnings:</b> {current_warns}/{MAX_WARNS}\n"
        f"📝 <b>Reason:</b> <i>{html.escape(reason)}</i></blockquote>",
        reply_markup=build_warn_buttons(target_id),
        parse_mode=ParseMode.HTML
    )
    await query.answer(f"Updated: {current_warns}/{MAX_WARNS}")

# ==================== UNWARN (COMMAND) ====================
@Client.on_message(filters.command(["unwarn"], prefixes=[".", "/"]) & filters.group)
async def unwarn_command(client: Client, message: Message):
    user_id = message.from_user.id if message.from_user else (message.sender_chat.id if message.sender_chat else 0)
    is_adm = await check_admin_sender(client, message.chat.id, user_id)
    if not is_adm:
        return await message.reply_text("<blockquote>❌ Sirf Admins hi unwarn kar sakte hain!</blockquote>", parse_mode=ParseMode.HTML)

    target = await extract_target(client, message)
    if not target:
        return await message.reply_text("<blockquote>⚠️ <b>User ke message par reply karein ya tag karein:</b> <code>.unwarn @username</code></blockquote>", parse_mode=ParseMode.HTML)

    if warns_db is None:
        return await message.reply_text("<blockquote>⚠️ Database connected nahi hai!</blockquote>", parse_mode=ParseMode.HTML)

    doc = await warns_db.find_one({"chat_id": message.chat.id, "user_id": target.id})
    if not doc or doc.get("count", 0) <= 0:
        return await message.reply_text("<blockquote>ℹ️ Is user ke paas pehle se koi warning nahi hai!</blockquote>", parse_mode=ParseMode.HTML)

    current_warns = doc.get("count", 1) - 1
    target_mention = get_user_mention(target)

    if current_warns <= 0:
        await warns_db.delete_one({"chat_id": message.chat.id, "user_id": target.id})
        await message.reply_text(
            f"<blockquote>✅ <b>Last Warn Removed!</b>\n"
            f"✦ ━━━━━━━━━━━━━━━━━━ ✦\n"
            f"👤 <b>User:</b> {target_mention}\n"
            f"✨ <i>Ab user ke paas 0 warnings hain (Database Cleared)!</i></blockquote>",
            parse_mode=ParseMode.HTML
        )
    else:
        await warns_db.update_one(
            {"chat_id": message.chat.id, "user_id": target.id},
            {"$set": {"count": current_warns}}
        )
        await message.reply_text(
            f"<blockquote>✅ <b>Last Warn Removed!</b>\n"
            f"✦ ━━━━━━━━━━━━━━━━━━ ✦\n"
            f"👤 <b>User:</b> {target_mention}\n"
            f"📊 <b>Remaining Warnings:</b> {current_warns}/{MAX_WARNS}\n"
            f"💾 <i>Updated in Database</i></blockquote>",
            reply_markup=build_warn_buttons(target.id),
            parse_mode=ParseMode.HTML
        )

# ==================== RMWARN / RESETWARNS (COMMAND) ====================
@Client.on_message(filters.command(["rmwarn", "resetwarns", "resetwarn"], prefixes=[".", "/"]) & filters.group)
async def rmwarn_command(client: Client, message: Message):
    user_id = message.from_user.id if message.from_user else (message.sender_chat.id if message.sender_chat else 0)
    is_adm = await check_admin_sender(client, message.chat.id, user_id)
    if not is_adm:
        return await message.reply_text("<blockquote>❌ Sirf Admins hi warnings remove kar sakte hain!</blockquote>", parse_mode=ParseMode.HTML)

    target = await extract_target(client, message)
    if not target:
        return await message.reply_text("<blockquote>⚠️ <b>User par reply karein ya tag karein:</b> <code>.rmwarn @username</code></blockquote>", parse_mode=ParseMode.HTML)

    if warns_db is not None:
        await warns_db.delete_one({"chat_id": message.chat.id, "user_id": target.id})

    target_mention = get_user_mention(target)
    await message.reply_text(
        f"<blockquote>🔄 <b>All Warnings Removed!</b>\n"
        f"✦ ━━━━━━━━━━━━━━━━━━ ✦\n"
        f"👤 <b>User:</b> {target_mention}\n"
        f"✨ <i>User ki saari warnings database se delete kar di gayi hain!</i></blockquote>",
        parse_mode=ParseMode.HTML
    )
    
