import os
from pyrogram import Client, filters
from pyrogram.types import ChatPermissions

OWNER_ID = int(os.environ.get("OWNER_ID"))

async def is_authorized(client, message):
    if message.from_user and message.from_user.id == OWNER_ID:
        return True
    try:
        member = await client.get_chat_member(message.chat.id, message.from_user.id)
        if member.status.name in ["OWNER", "ADMINISTRATOR"]:
            return True
    except Exception:
        pass
    return False

# ==================== BAN COMMAND ====================
@Client.on_message(filters.command("ban", prefixes=[".", "/"]) & filters.group)
async def ban_user(client, message):
    if not await is_authorized(client, message):
        return

    target = None
    if message.reply_to_message:
        target = message.reply_to_message.from_user
    elif len(message.command) > 1:
        user_input = message.command[1]
        try:
            target = await client.get_users(user_input)
        except Exception as e:
            return await message.reply_text(f"User nahi mila: `{e}`")

    if not target:
        return await message.reply_text("Kisi ke message par reply karke `.ban` likhein ya username/ID dein.")

    try:
        await client.ban_chat_member(message.chat.id, target.id)
        mention = f"[{target.first_name}](tg://user?id={target.id})"
        await message.reply_text(f"🚫 {mention} ko group se **Ban** kar diya gaya!")
    except Exception as e:
        await message.reply_text(f"Ban karne mein error aayi:\n`{e}`")

# ==================== UNBAN COMMAND ====================
@Client.on_message(filters.command("unban", prefixes=[".", "/"]) & filters.group)
async def unban_user(client, message):
    if not await is_authorized(client, message):
        return

    target = None
    if message.reply_to_message:
        target = message.reply_to_message.from_user
    elif len(message.command) > 1:
        user_input = message.command[1]
        try:
            target = await client.get_users(user_input)
        except Exception as e:
            return await message.reply_text(f"User nahi mila: `{e}`")

    if not target:
        return await message.reply_text("Kisi ke message par reply karke `.unban` likhein ya username/ID dein.")

    try:
        await client.unban_chat_member(message.chat.id, target.id)
        mention = f"[{target.first_name}](tg://user?id={target.id})"
        await message.reply_text(f"✅ {mention} ko **Unban** kar diya gaya!")
    except Exception as e:
        await message.reply_text(f"Unban karne mein error aayi:\n`{e}`")

# ==================== KICK COMMAND ====================
@Client.on_message(filters.command("kick", prefixes=[".", "/"]) & filters.group)
async def kick_user(client, message):
    if not await is_authorized(client, message):
        return

    target = None
    if message.reply_to_message:
        target = message.reply_to_message.from_user
    elif len(message.command) > 1:
        user_input = message.command[1]
        try:
            target = await client.get_users(user_input)
        except Exception as e:
            return await message.reply_text(f"User nahi mila: `{e}`")

    if not target:
        return await message.reply_text("Kisi ke message par reply karke `.kick` likhein ya username/ID dein.")

    try:
        # Telegram API mein kick karne ke liye pehle ban karke turant unban karte hain
        await client.ban_chat_member(message.chat.id, target.id)
        await client.unban_chat_member(message.chat.id, target.id)
        mention = f"[{target.first_name}](tg://user?id={target.id})"
        await message.reply_text(f"👢 {mention} ko group se **Kick** kar diya gaya!")
    except Exception as e:
        await message.reply_text(f"Kick karne mein error aayi:\n`{e}`")

# ==================== DELETE MESSAGE COMMAND ====================
@Client.on_message(filters.command("del", prefixes=[".", "/"]) & filters.group)
async def delete_message(client, message):
    if not await is_authorized(client, message):
        return

    if message.reply_to_message:
        try:
            await message.reply_to_message.delete()
            await message.delete()
        except Exception as e:
            await message.reply_text(f"Message delete nahi ho paya:\n`{e}`")
      
