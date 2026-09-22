import re
from pyrogram import Client, filters
from pyrogram.types import ChatPrivileges, ChatPermissions

ITACHI_ID = 8373739674

async def is_authorized(client, message):
    if not message.from_user:
        return False
    if message.from_user.id == ITACHI_ID:
        return True
    try:
        member = await client.get_chat_member(message.chat.id, message.from_user.id)
        if member.status.name in ["OWNER", "ADMINISTRATOR"]:
            return True
    except Exception:
        pass
    return False

def get_target(message):
    if message.reply_to_message and message.reply_to_message.from_user:
        return message.reply_to_message.from_user
    return None

# ==================== PROMOTE ====================
@Client.on_message(filters.command("promote", prefixes=[".", "/"]) & filters.group)
async def promote_cmd(client, message):
    if not await is_authorized(client, message):
        return
    target = get_target(message)
    if not target:
        return await message.reply_text("⚠️ Kisi ke message par reply karke `.promote <title>` likhein.")

    parts = message.text.split(maxsplit=1)
    title = parts[1][:16] if len(parts) > 1 else "Admin"

    try:
        await client.promote_chat_member(
            chat_id=message.chat.id,
            user_id=target.id,
            privileges=ChatPrivileges(
                can_manage_chat=True,
                can_delete_messages=True,
                can_restrict_members=True,
                can_invite_users=True,
                can_pin_messages=True,
                can_manage_video_chats=True,
                can_promote_members=True
            )
        )
        try:
            await client.set_administrator_title(message.chat.id, target.id, title)
        except Exception:
            pass
        name = re.sub(r'[*_`\[\]()]', '', target.first_name or "User")
        await message.reply_text(f"👑 [{name}](tg://user?id={target.id}) ko Promote kar diya gaya!\n**Title:** `{title}`")
    except Exception as e:
        await message.reply_text(f"❌ Promote error: `{e}`")

# ==================== DEMOTE ====================
@Client.on_message(filters.command("demote", prefixes=[".", "/"]) & filters.group)
async def demote_cmd(client, message):
    if not await is_authorized(client, message):
        return
    target = get_target(message)
    if not target:
        return await message.reply_text("⚠️ Kisi admin ke message par reply karke `.demote` likhein.")

    try:
        await client.promote_chat_member(
            chat_id=message.chat.id,
            user_id=target.id,
            privileges=ChatPrivileges()
        )
        name = re.sub(r'[*_`\[\]()]', '', target.first_name or "User")
        await message.reply_text(f"📉 [{name}](tg://user?id={target.id}) ko Demote kar diya gaya!")
    except Exception as e:
        await message.reply_text(f"❌ Demote error: `{e}`")

# ==================== BAN ====================
@Client.on_message(filters.command("ban", prefixes=[".", "/"]) & filters.group)
async def ban_cmd(client, message):
    if not await is_authorized(client, message):
        return
    target = get_target(message)
    if not target:
        return await message.reply_text("⚠️ Kisi user ke message par reply karke `.ban` likhein.")

    try:
        await client.ban_chat_member(message.chat.id, target.id)
        name = re.sub(r'[*_`\[\]()]', '', target.first_name or "User")
        await message.reply_text(f"🚫 [{name}](tg://user?id={target.id}) ko Ban kar diya gaya!")
    except Exception as e:
        await message.reply_text(f"❌ Ban error: `{e}`")

# ==================== KICK ====================
@Client.on_message(filters.command("kick", prefixes=[".", "/"]) & filters.group)
async def kick_cmd(client, message):
    if not await is_authorized(client, message):
        return
    target = get_target(message)
    if not target:
        return await message.reply_text("⚠️ Kisi user ke message par reply karke `.kick` likhein.")

    try:
        await client.ban_chat_member(message.chat.id, target.id)
        await client.unban_chat_member(message.chat.id, target.id)
        name = re.sub(r'[*_`\[\]()]', '', target.first_name or "User")
        await message.reply_text(f"👢 [{name}](tg://user?id={target.id}) ko Kick kar diya gaya!")
    except Exception as e:
        await message.reply_text(f"❌ Kick error: `{e}`")

# ==================== MUTE ====================
@Client.on_message(filters.command("mute", prefixes=[".", "/"]) & filters.group)
async def mute_cmd(client, message):
    if not await is_authorized(client, message):
        return
    target = get_target(message)
    if not target:
        return await message.reply_text("⚠️ Kisi user ke message par reply karke `.mute` likhein.")

    try:
        await client.restrict_chat_member(
            chat_id=message.chat.id,
            user_id=target.id,
            permissions=ChatPermissions(can_send_messages=False)
        )
        name = re.sub(r'[*_`\[\]()]', '', target.first_name or "User")
        await message.reply_text(f"🔇 [{name}](tg://user?id={target.id}) ko Mute kar diya gaya!")
    except Exception as e:
        await message.reply_text(f"❌ Mute error: `{e}`")

# ==================== UNMUTE ====================
@Client.on_message(filters.command("unmute", prefixes=[".", "/"]) & filters.group)
async def unmute_cmd(client, message):
    if not await is_authorized(client, message):
        return
    target = get_target(message)
    if not target:
        return await message.reply_text("⚠️ Kisi user ke message par reply karke `.unmute` likhein.")

    try:
        await client.restrict_chat_member(
            chat_id=message.chat.id,
            user_id=target.id,
            permissions=ChatPermissions(
                can_send_messages=True,
                can_send_media_messages=True,
                can_send_other_messages=True,
                can_add_web_page_previews=True
            )
        )
        name = re.sub(r'[*_`\[\]()]', '', target.first_name or "User")
        await message.reply_text(f"🔊 [{name}](tg://user?id={target.id}) ko Unmute kar diya gaya!")
    except Exception as e:
        await message.reply_text(f"❌ Unmute error: `{e}`")
        
