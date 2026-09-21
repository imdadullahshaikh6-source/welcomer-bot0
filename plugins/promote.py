import os
from pyrogram import Client, filters
from pyrogram.types import ChatPrivileges

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

# ==================== PROMOTE COMMAND ====================
@Client.on_message(filters.command("promote", prefixes=[".", "/"]) & filters.group)
async def promote_user(client, message):
    if not await is_authorized(client, message):
        return

    target = None
    custom_title = "Admin"

    if message.reply_to_message:
        target = message.reply_to_message.from_user
        if len(message.command) > 1:
            custom_title = message.text.split(None, 1)[1]
    elif len(message.command) > 1:
        args = message.command
        try:
            target = await client.get_users(args[1])
            if len(args) > 2:
                custom_title = message.text.split(None, 2)[2]
        except Exception as e:
            return await message.reply_text(f"User nahi mila: `{e}`")

    if not target:
        return await message.reply_text("Kisi user ke message par reply karein ya format use karein:\n`.promote @username Title`")

    # Title 16 characters se zyada nahi ho sakta (Telegram restriction)
    custom_title = custom_title[:16]

    try:
        await client.promote_chat_member(
            chat_id=message.chat.id,
            user_id=target.id,
            privileges=ChatPrivileges(
                can_change_info=False,
                can_post_messages=False,
                can_edit_messages=False,
                can_delete_messages=True,
                can_restrict_members=True,
                can_invite_users=True,
                can_pin_messages=True,
                can_manage_video_chats=True
            )
        )
        try:
            await client.set_administrator_title(message.chat.id, target.id, custom_title)
        except Exception:
            pass

        mention = f"[{target.first_name}](tg://user?id={target.id})"
        await message.reply_text(f"👑 {mention} ko Promote kar diya gaya!\n**Custom Title:** `{custom_title}`")
    except Exception as e:
        await message.reply_text(f"Promote karne mein error aayi:\n`{e}`")

# ==================== DEMOTE COMMAND ====================
@Client.on_message(filters.command("demote", prefixes=[".", "/"]) & filters.group)
async def demote_user(client, message):
    if not await is_authorized(client, message):
        return

    target = None
    if message.reply_to_message:
        target = message.reply_to_message.from_user
    elif len(message.command) > 1:
        try:
            target = await client.get_users(message.command[1])
        except Exception as e:
            return await message.reply_text(f"User nahi mila: `{e}`")

    if not target:
        return await message.reply_text("Kisi admin ke message par reply karke `.demote` likhein.")

    try:
        await client.promote_chat_member(
            chat_id=message.chat.id,
            user_id=target.id,
            privileges=ChatPrivileges(
                can_change_info=False,
                can_post_messages=False,
                can_edit_messages=False,
                can_delete_messages=False,
                can_restrict_members=False,
                can_invite_users=False,
                can_pin_messages=False,
                can_manage_video_chats=False,
                can_promote_members=False
            )
        )
        mention = f"[{target.first_name}](tg://user?id={target.id})"
        await message.reply_text(f"📉 {mention} ko Demote (admin se hata) diya gaya!")
    except Exception as e:
        await message.reply_text(f"Demote karne mein error aayi:\n`{e}`")
  
