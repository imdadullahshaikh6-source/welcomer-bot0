import re
from pyrogram import Client, filters
from pyrogram.types import (
    ChatPrivileges,
    ChatPermissions,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery
)

ITACHI_ID = 8373739674

async def is_authorized(client, user_id, chat_id):
    if user_id == ITACHI_ID:
        return True
    try:
        member = await client.get_chat_member(chat_id, user_id)
        if member.status.name in ["OWNER", "ADMINISTRATOR"]:
            return True
    except Exception:
        pass
    return False

def get_target(message):
    if message.reply_to_message and message.reply_to_message.from_user:
        return message.reply_to_message.from_user
    return None

def clean_txt(text: str) -> str:
    return re.sub(r'[*_`\[\]()]', '', text or "User")

# Standard empty privileges for clean demote
DEMOTE_PRIVILEGES = ChatPrivileges(
    can_manage_chat=False,
    can_delete_messages=False,
    can_restrict_members=False,
    can_invite_users=False,
    can_pin_messages=False,
    can_manage_video_chats=False,
    can_promote_members=False
)

# ==================== PROMOTE COMMAND ====================
@Client.on_message(filters.command("promote", prefixes=[".", "/"]) & filters.group)
async def promote_cmd(client, message):
    if not message.from_user or not await is_authorized(client, message.from_user.id, message.chat.id):
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

        admin_name = clean_txt(message.from_user.first_name)
        target_name = clean_txt(target.first_name)

        text = (
            "✦ ━━━━━━━━━━━━━━━━━━ ✦\n"
            "✨ 𝙥𝙧𝙤𝙢𝙤𝙩𝙚 𝙚𝙫𝙚𝙣𝙩 ✨\n"
            "✦ ━━━━━━━━━━━━━━━━━━ ✦\n\n"
            f"👤 **User:** [{target_name}](tg://user?id={target.id})\n"
            f"🆔 **User ID:** `{target.id}`\n"
            f"🏷️ **Custom Title:** `{title}`\n"
            f"👑 **Promoted By:** [{admin_name}](tg://user?id={message.from_user.id})\n"
            f"⚡ **Status:** Successfully Promoted!"
        )

        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("📉 Demote User", callback_data=f"demote_{target.id}_{message.from_user.id}")]
        ])

        await message.reply_text(text=text, reply_markup=keyboard)
    except Exception as e:
        await message.reply_text(f"❌ Promote error: `{e}`")

# ==================== DEMOTE COMMAND ====================
@Client.on_message(filters.command("demote", prefixes=[".", "/"]) & filters.group)
async def demote_cmd(client, message):
    if not message.from_user or not await is_authorized(client, message.from_user.id, message.chat.id):
        return

    target = get_target(message)
    if not target:
        return await message.reply_text("⚠️ Kisi admin ke message par reply karke `.demote` likhein.")

    try:
        await client.promote_chat_member(
            chat_id=message.chat.id,
            user_id=target.id,
            privileges=DEMOTE_PRIVILEGES
        )
        admin_name = clean_txt(message.from_user.first_name)
        target_name = clean_txt(target.first_name)

        text = (
            "✦ ━━━━━━━━━━━━━━━━━━ ✦\n"
            "📉 𝙙𝙚𝙢𝙤𝙩𝙚 𝙚𝙫𝙚𝙣𝙩 📉\n"
            "✦ ━━━━━━━━━━━━━━━━━━ ✦\n\n"
            f"👤 **User:** [{target_name}](tg://user?id={target.id})\n"
            f"🆔 **User ID:** `{target.id}`\n"
            f"👮 **Demoted By:** [{admin_name}](tg://user?id={message.from_user.id})\n"
            f"⚡ **Status:** Admin Rights Removed!"
        )
        await message.reply_text(text=text)
    except Exception as e:
        await message.reply_text(f"❌ Demote error: `{e}`")

# ==================== MUTE COMMAND ====================
@Client.on_message(filters.command("mute", prefixes=[".", "/"]) & filters.group)
async def mute_cmd(client, message):
    if not message.from_user or not await is_authorized(client, message.from_user.id, message.chat.id):
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
        admin_name = clean_txt(message.from_user.first_name)
        target_name = clean_txt(target.first_name)

        text = (
            "✦ ━━━━━━━━━━━━━━━━━━ ✦\n"
            "🔇 𝙢𝙪𝙩𝙚 𝙚𝙫𝙚𝙣𝙩 🔇\n"
            "✦ ━━━━━━━━━━━━━━━━━━ ✦\n\n"
            f"👤 **User:** [{target_name}](tg://user?id={target.id})\n"
            f"🆔 **User ID:** `{target.id}`\n"
            f"👮 **Muted By:** [{admin_name}](tg://user?id={message.from_user.id})\n"
            f"⚡ **Status:** Muted indefinitely!"
        )

        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔊 Unmute User", callback_data=f"unmute_{target.id}_{message.from_user.id}")]
        ])

        await message.reply_text(text=text, reply_markup=keyboard)
    except Exception as e:
        await message.reply_text(f"❌ Mute error: `{e}`")

# ==================== UNMUTE COMMAND ====================
@Client.on_message(filters.command("unmute", prefixes=[".", "/"]) & filters.group)
async def unmute_cmd(client, message):
    if not message.from_user or not await is_authorized(client, message.from_user.id, message.chat.id):
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
        admin_name = clean_txt(message.from_user.first_name)
        target_name = clean_txt(target.first_name)

        text = (
            "✦ ━━━━━━━━━━━━━━━━━━ ✦\n"
            "🔊 𝙪𝙣𝙢𝙪𝙩𝙚 𝙚𝙫𝙚𝙣𝙩 🔊\n"
            "✦ ━━━━━━━━━━━━━━━━━━ ✦\n\n"
            f"👤 **User:** [{target_name}](tg://user?id={target.id})\n"
            f"🆔 **User ID:** `{target.id}`\n"
            f"👮 **Unmuted By:** [{admin_name}](tg://user?id={message.from_user.id})\n"
            f"⚡ **Status:** Successfully Unmuted!"
        )
        await message.reply_text(text=text)
    except Exception as e:
        await message.reply_text(f"❌ Unmute error: `{e}`")

# ==================== BAN & KICK ====================
@Client.on_message(filters.command("ban", prefixes=[".", "/"]) & filters.group)
async def ban_cmd(client, message):
    if not message.from_user or not await is_authorized(client, message.from_user.id, message.chat.id):
        return
    target = get_target(message)
    if not target:
        return await message.reply_text("⚠️ Kisi user ke message par reply karke `.ban` likhein.")
    try:
        await client.ban_chat_member(message.chat.id, target.id)
        target_name = clean_txt(target.first_name)
        await message.reply_text(f"🚫 [{target_name}](tg://user?id={target.id}) ko permanently **BAN** kar diya gaya!")
    except Exception as e:
        await message.reply_text(f"❌ Ban error: `{e}`")

@Client.on_message(filters.command("kick", prefixes=[".", "/"]) & filters.group)
async def kick_cmd(client, message):
    if not message.from_user or not await is_authorized(client, message.from_user.id, message.chat.id):
        return
    target = get_target(message)
    if not target:
        return await message.reply_text("⚠️ Kisi user ke message par reply karke `.kick` likhein.")
    try:
        await client.ban_chat_member(message.chat.id, target.id)
        await client.unban_chat_member(message.chat.id, target.id)
        target_name = clean_txt(target.first_name)
        await message.reply_text(f"👢 [{target_name}](tg://user?id={target.id}) ko **KICK** kar diya gaya!")
    except Exception as e:
        await message.reply_text(f"❌ Kick error: `{e}`")

# ==================== BUTTON CALLBACKS ====================
@Client.on_callback_query(filters.regex(r"^(demote|unmute|mute)_(\d+)_(\d+)$"))
async def admin_buttons_callback(client, query: CallbackQuery):
    action, target_id, by_user_id = query.data.split("_")
    target_id = int(target_id)
    by_user_id = int(by_user_id)
    caller_id = query.from_user.id

    if caller_id != by_user_id and caller_id != ITACHI_ID:
        return await query.answer("❌ Yeh button sirf command dene wale Admin ke liye hai!", show_alert=True)

    try:
        target_user = await client.get_users(target_id)
        target_name = clean_txt(target_user.first_name)
    except Exception:
        target_name = "User"

    caller_name = clean_txt(query.from_user.first_name)

    if action == "demote":
        try:
            await client.promote_chat_member(
                chat_id=query.message.chat.id,
                user_id=target_id,
                privileges=DEMOTE_PRIVILEGES
            )
            updated_text = (
                "✦ ━━━━━━━━━━━━━━━━━━ ✦\n"
                "📉 𝙙𝙚𝙢𝙤𝙩𝙚 𝙚𝙫𝙚𝙣𝙩 📉\n"
                "✦ ━━━━━━━━━━━━━━━━━━ ✦\n\n"
                f"👤 **User:** [{target_name}](tg://user?id={target_id})\n"
                f"🆔 **User ID:** `{target_id}`\n"
                f"👮 **Demoted By:** [{caller_name}](tg://user?id={caller_id})\n"
                f"⚡ **Status:** Demoted via Quick Button!"
            )
            await query.message.edit_text(text=updated_text, reply_markup=None)
            await query.answer("✅ User ko demote kar diya gaya!")
        except Exception as e:
            await query.answer(f"Demote failed: {e}", show_alert=True)

    elif action == "unmute":
        try:
            await client.restrict_chat_member(
                chat_id=query.message.chat.id,
                user_id=target_id,
                permissions=ChatPermissions(
                    can_send_messages=True,
                    can_send_media_messages=True,
                    can_send_other_messages=True,
                    can_add_web_page_previews=True
                )
            )
            updated_text = (
                "✦ ━━━━━━━━━━━━━━━━━━ ✦\n"
                "🔊 𝙪𝙣𝙢𝙪𝙩𝙚 𝙚𝙫𝙚𝙣𝙩 🔊\n"
                "✦ ━━━━━━━━━━━━━━━━━━ ✦\n\n"
                f"👤 **User:** [{target_name}](tg://user?id={target_id})\n"
                f"🆔 **User ID:** `{target_id}`\n"
                f"👮 **Unmuted By:** [{caller_name}](tg://user?id={caller_id})\n"
                f"⚡ **Status:** Unmuted via Quick Button!"
            )
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("🔇 Mute Again", callback_data=f"mute_{target_id}_{caller_id}")]
            ])
            await query.message.edit_text(text=updated_text, reply_markup=keyboard)
            await query.answer("✅ User ko unmute kar diya gaya!")
        except Exception as e:
            await query.answer(f"Unmute failed: {e}", show_alert=True)

    elif action == "mute":
        try:
            await client.restrict_chat_member(
                chat_id=query.message.chat.id,
                user_id=target_id,
                permissions=ChatPermissions(can_send_messages=False)
            )
            updated_text = (
                "✦ ━━━━━━━━━━━━━━━━━━ ✦\n"
                "🔇 𝙢𝙪𝙩𝙚 𝙚𝙫𝙚𝙣𝙩 🔇\n"
                "✦ ━━━━━━━━━━━━━━━━━━ ✦\n\n"
                f"👤 **User:** [{target_name}](tg://user?id={target_id})\n"
                f"🆔 **User ID:** `{target_id}`\n"
                f"👮 **Muted By:** [{caller_name}](tg://user?id={caller_id})\n"
                f"⚡ **Status:** Muted via Quick Button!"
            )
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("🔊 Unmute User", callback_data=f"unmute_{target_id}_{caller_id}")]
            ])
            await query.message.edit_text(text=updated_text, reply_markup=keyboard)
            await query.answer("✅ User ko wapas mute kar diya gaya!")
        except Exception as e:
            await query.answer(f"Mute failed: {e}", show_alert=True)
            
