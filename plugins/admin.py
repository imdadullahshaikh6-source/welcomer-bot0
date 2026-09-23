import os
import html
from pyrogram import Client, filters
from pyrogram.enums import ParseMode, ChatMemberStatus, MessageEntityType
from pyrogram.types import Message
from motor.motor_asyncio import AsyncIOMotorClient

# MongoDB Connection
MONGO_URL = os.environ.get("MONGO_URL") or os.environ.get("DATABASE_URL")
if MONGO_URL:
    mongo_client = AsyncIOMotorClient(MONGO_URL)
    db = mongo_client.get_database("WelcomerBot")
    banned_db = db.banned_users
else:
    banned_db = None

async def save_ban_to_db(chat_id: int, user_id: int, admin_id: int, reason: str):
    if banned_db is not None:
        try:
            await banned_db.update_one(
                {"chat_id": chat_id, "user_id": user_id},
                {"$set": {"admin_id": admin_id, "reason": reason}},
                upsert=True
            )
        except Exception:
            pass

async def remove_ban_from_db(chat_id: int, user_id: int):
    if banned_db is not None:
        try:
            await banned_db.delete_one({"chat_id": chat_id, "user_id": user_id})
        except Exception:
            pass

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

# ==================== BAN ====================
@Client.on_message(filters.command(["ban", "dban"], prefixes=[".", "/"]) & filters.group)
async def ban_command(client: Client, message: Message):
    if not message.from_user:
        return

    is_adm, privs = await get_admin_privileges(client, message.from_user.id, message.chat.id)
    if not is_adm:
        return

    if privs != "owner" and not (privs and privs.can_restrict_members):
        return await message.reply_text(
            "<blockquote>❌ <b>Permission Denied!</b>\nAapke paas Ban Users right nahi hai.</blockquote>",
            parse_mode=ParseMode.HTML
        )

    target = await extract_target_user(client, message)
    if not target:
        return await message.reply_text(
            "<blockquote>⚠️ <b>Kisi user/bot ke message par reply karein ya tag karein:</b> <code>.ban @username</code></blockquote>",
            parse_mode=ParseMode.HTML
        )

    bot = await client.get_me()
    if target.id == bot.id:
        return await message.reply_text("<blockquote>🥺 Main khud ko ban nahi kar sakti!</blockquote>", parse_mode=ParseMode.HTML)

    target_is_adm, _ = await get_admin_privileges(client, target.id, message.chat.id)
    if target_is_adm:
        return await message.reply_text("<blockquote>⚠️ Main kisi doosre admin ko ban nahi kar sakti!</blockquote>", parse_mode=ParseMode.HTML)

    parts = message.text.split(maxsplit=2)
    reason = "None"
    if message.reply_to_message and len(parts) > 1:
        reason = message.text.split(maxsplit=1)[1]
    elif not message.reply_to_message and len(parts) > 2:
        reason = parts[2]

    try:
        await client.ban_chat_member(message.chat.id, target.id)
        await save_ban_to_db(message.chat.id, target.id, message.from_user.id, reason)

        mention = get_user_mention(target)
        admin_mention = get_user_mention(message.from_user)

        if message.command[0].lower() == "dban" and message.reply_to_message:
            try:
                await message.reply_to_message.delete()
            except Exception:
                pass

        await message.reply_text(
            f"<blockquote>🚫 <b>Banned User!</b>\n"
            f"✦ ━━━━━━━━━━━━━━━━━━ ✦\n"
            f"👤 <b>Target:</b> {mention} [<code>{target.id}</code>]\n"
            f"👮‍♂️ <b>Admin:</b> {admin_mention}\n"
            f"📝 <b>Reason:</b> <i>{html.escape(reason)}</i>\n"
            f"💾 <i>Saved to Database</i></blockquote>",
            parse_mode=ParseMode.HTML
        )
    except Exception as e:
        await message.reply_text(
            f"<blockquote>⚠️ <b>Failed to ban:</b> <code>{html.escape(str(e))}</code></blockquote>",
            parse_mode=ParseMode.HTML
        )

# ==================== KICK ====================
@Client.on_message(filters.command(["kick", "dkick"], prefixes=[".", "/"]) & filters.group)
async def kick_command(client: Client, message: Message):
    if not message.from_user:
        return

    is_adm, privs = await get_admin_privileges(client, message.from_user.id, message.chat.id)
    if not is_adm:
        return

    if privs != "owner" and not (privs and privs.can_restrict_members):
        return await message.reply_text(
            "<blockquote>❌ <b>Permission Denied!</b>\nAapke paas Ban Users right nahi hai.</blockquote>",
            parse_mode=ParseMode.HTML
        )

    target = await extract_target_user(client, message)
    if not target:
        return await message.reply_text(
            "<blockquote>⚠️ <b>Kisi user/bot ke message par reply karein ya tag karein:</b> <code>.kick @username</code></blockquote>",
            parse_mode=ParseMode.HTML
        )

    bot = await client.get_me()
    if target.id == bot.id:
        return await message.reply_text("<blockquote>🥺 Main khud ko kick nahi kar sakti!</blockquote>", parse_mode=ParseMode.HTML)

    target_is_adm, _ = await get_admin_privileges(client, target.id, message.chat.id)
    if target_is_adm:
        return await message.reply_text("<blockquote>⚠️ Main kisi admin ko kick nahi kar sakti!</blockquote>", parse_mode=ParseMode.HTML)

    parts = message.text.split(maxsplit=2)
    reason = "None"
    if message.reply_to_message and len(parts) > 1:
        reason = message.text.split(maxsplit=1)[1]
    elif not message.reply_to_message and len(parts) > 2:
        reason = parts[2]

    try:
        await client.ban_chat_member(message.chat.id, target.id)
        await client.unban_chat_member(message.chat.id, target.id)

        mention = get_user_mention(target)
        admin_mention = get_user_mention(message.from_user)

        if message.command[0].lower() == "dkick" and message.reply_to_message:
            try:
                await message.reply_to_message.delete()
            except Exception:
                pass

        await message.reply_text(
            f"<blockquote>👢 <b>Kicked User!</b>\n"
            f"✦ ━━━━━━━━━━━━━━━━━━ ✦\n"
            f"👤 <b>Target:</b> {mention} [<code>{target.id}</code>]\n"
            f"👮‍♂️ <b>Admin:</b> {admin_mention}\n"
            f"📝 <b>Reason:</b> <i>{html.escape(reason)}</i></blockquote>",
            parse_mode=ParseMode.HTML
        )
    except Exception as e:
        await message.reply_text(
            f"<blockquote>⚠️ <b>Failed to kick:</b> <code>{html.escape(str(e))}</code></blockquote>",
            parse_mode=ParseMode.HTML
        )

# ==================== UNBAN ====================
@Client.on_message(filters.command(["unban"], prefixes=[".", "/"]) & filters.group)
async def unban_command(client: Client, message: Message):
    if not message.from_user:
        return

    is_adm, privs = await get_admin_privileges(client, message.from_user.id, message.chat.id)
    if not is_adm:
        return

    if privs != "owner" and not (privs and privs.can_restrict_members):
        return await message.reply_text(
            "<blockquote>❌ <b>Permission Denied!</b>\nAapke paas Ban Users right nahi hai.</blockquote>",
            parse_mode=ParseMode.HTML
        )

    target = await extract_target_user(client, message)
    if not target:
        return await message.reply_text(
            "<blockquote>⚠️ <b>User ID/tag specify karein ya reply karein:</b> <code>.unban @username</code></blockquote>",
            parse_mode=ParseMode.HTML
        )

    try:
        await client.unban_chat_member(message.chat.id, target.id)
        await remove_ban_from_db(message.chat.id, target.id)

        mention = get_user_mention(target)
        await message.reply_text(
            f"<blockquote>✅ <b>Unbanned!</b>\n"
            f"✦ ━━━━━━━━━━━━━━━━━━ ✦\n"
            f"👤 <b>User:</b> {mention}\n"
            f"✨ <i>Database se removed & unbanned!</i></blockquote>",
            parse_mode=ParseMode.HTML
        )
    except Exception as e:
        await message.reply_text(
            f"<blockquote>⚠️ <b>Failed to unban:</b> <code>{html.escape(str(e))}</code></blockquote>",
            parse_mode=ParseMode.HTML
        )
        
