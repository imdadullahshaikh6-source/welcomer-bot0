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
    return re.sub(r'[*_`\[\]()<>]', '', text or "User")

DEMOTE_PRIVILEGES = ChatPrivileges(
    can_manage_chat=False,
    can_delete_messages=False,
    can_restrict_members=False,
    can_invite_users=False,
    can_pin_messages=False,
    can_manage_video_chats=False,
    can_promote_members=False
)

# ==================== PROMOTE ====================
@Client.on_message(filters.command("promote", prefixes=[".", "/"]) & filters.group)
async def promote_cmd(client, message):
    if not message.from_user or not await is_authorized(client, message.from_user.id, message.chat.id):
        return

    target = get_target(message)
    if not target:
        return await message.reply_text("<blockquote>⚠️ <b>Kisi ke message par reply karke <code>.promote &lt;title&gt;</code> likhein.</b></blockquote>")

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
            "<blockquote>✨ <b>𝙥𝙧𝙤𝙢𝙤𝙩𝙚 𝙚𝙫𝙚𝙣𝙩</b> ✨\n"
            "✦ ━━━━━━━━━━━━━━━━━━ ✦\n"
            f"👤 <b>User:</b> <a href='tg://user?id={target.id}'>{target_name}</a>\n"
            f"🆔 <b>User ID:</b> <code>{target.id}</code>\n"
            f"🏷️ <b>Custom Title:</b> <code>{title}</code>\n"
            f"👑 <b>Promoted By:</b> <a href='tg://user?id={message.from_user.id}'>{admin_name}</a>\n"
            "⚡ <b>Status:</b> Successfully Promoted!</blockquote>"
        )

        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("📉 Demote User", callback_data=f"demote_{target.id}_{message.from_user.id}")]
        ])

        await message.reply_text(text=text, reply_markup=keyboard)
    except Exception as e:
        await message.reply_text(f"<blockquote>❌ <b>Promote error:</b> <code>{e}</code></blockquote>")

# ==================== DEMOTE ====================
@Client.on_message(filters.command("demote", prefixes=[".", "/"]) & filters.group)
async def demote_cmd(client, message):
    if not message.from_user or not await is_authorized(client, message.from_user.id, message.chat.id):
        return

    target = get_target(message)
    if not target:
        return await message.reply_text("<blockquote>⚠️ <b>Kisi admin ke message par reply karke <code>.demote</code> likhein.</b></blockquote>")

    try:
        await client.promote_chat_member(
            chat_id=message.chat.id,
            user_id=target.id,
            privileges=DEMOTE_PRIVILEGES
        )
        admin_name = clean_txt(message.from_user.first_name)
        target_name = clean_txt(target.first_name)

        text = (
            "<blockquote>📉 <b>𝙙𝙚𝙢𝙤𝙩𝙚 𝙚𝙫𝙚𝙣𝙩</b> 📉\n"
            "✦ ━━━━━━━━━━━━━━━━━━ ✦\n"
            f"👤 <b>User:</b> <a href='tg://user?id={target.id}'>{target_name}</a>\n"
            f"🆔 <b>User ID:</b> <code>{target.id}</code>\n"
            f"👮 <b>Demoted By:</b> <a href='tg://user?id={message.from_user.id}'>{admin_name}</a>\n"
            "⚡ <b>Status:</b> Admin Rights Removed!</blockquote>"
        )
        await message.reply_text(text=text)
    except Exception as e:
        await message.reply_text(f"<blockquote>❌ <b>Demote error:</b> <code>{e}</code></blockquote>")

# ==================== PIN COMMANDS ====================
@Client.on_message(filters.command("pin", prefixes=[".", "/"]) & filters.group)
async def pin_cmd(client, message):
    if not message.from_user or not await is_authorized(client, message.from_user.id, message.chat.id):
        return

    if not message.reply_to_message:
        return await message.reply_text("<blockquote>⚠️ <b>Kisi message par reply karke <code>.pin</code> likhein.</b></blockquote>")

    # Check notification toggle (.pin loud)
    disable_notification = True
    if len(message.command) > 1 and message.command[1].lower() in ["loud", "notify"]:
        disable_notification = False

    try:
        await client.pin_chat_message(
            chat_id=message.chat.id,
            message_id=message.reply_to_message.id,
            disable_notification=disable_notification
        )

        admin_name = clean_txt(message.from_user.first_name)
        mode = "Loud (With Notification)" if not disable_notification else "Silent"

        text = (
            "<blockquote>📌 <b>𝙥𝙞𝙣 𝙚𝙫𝙚𝙣𝙩</b> 📌\n"
            "✦ ━━━━━━━━━━━━━━━━━━ ✦\n"
            f"👮 <b>Pinned By:</b> <a href='tg://user?id={message.from_user.id}'>{admin_name}</a>\n"
            f"🔔 <b>Notification:</b> <code>{mode}</code>\n"
            "⚡ <b>Status:</b> Message Successfully Pinned!</blockquote>"
        )

        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("📍 Unpin Message", callback_data=f"unpinmsg_{message.reply_to_message.id}_{message.from_user.id}")]
        ])

        await message.reply_text(text=text, reply_markup=keyboard)
    except Exception as e:
        await message.reply_text(f"<blockquote>❌ <b>Pin Error:</b> <code>{e}</code></blockquote>")

@Client.on_message(filters.command("unpin", prefixes=[".", "/"]) & filters.group)
async def unpin_cmd(client, message):
    if not message.from_user or not await is_authorized(client, message.from_user.id, message.chat.id):
        return

    if not message.reply_to_message:
        return await message.reply_text("<blockquote>⚠️ <b>Kisi pinned message par reply karke <code>.unpin</code> likhein.</b></blockquote>")

    try:
        await client.unpin_chat_message(
            chat_id=message.chat.id,
            message_id=message.reply_to_message.id
        )
        admin_name = clean_txt(message.from_user.first_name)
        text = (
            "<blockquote>📍 <b>𝙪𝙣𝙥𝙞𝙣 𝙚𝙫𝙚𝙣𝙩</b> 📍\n"
            "✦ ━━━━━━━━━━━━━━━━━━ ✦\n"
            f"👮 <b>Unpinned By:</b> <a href='tg://user?id={message.from_user.id}'>{admin_name}</a>\n"
            "⚡ <b>Status:</b> Message Unpinned!</blockquote>"
        )
        await message.reply_text(text=text)
    except Exception as e:
        await message.reply_text(f"<blockquote>❌ <b>Unpin Error:</b> <code>{e}</code></blockquote>")

@Client.on_message(filters.command("unpinall", prefixes=[".", "/"]) & filters.group)
async def unpinall_cmd(client, message):
    if not message.from_user or not await is_authorized(client, message.from_user.id, message.chat.id):
        return

    try:
        await client.unpin_all_chat_messages(chat_id=message.chat.id)
        admin_name = clean_txt(message.from_user.first_name)
        text = (
            "<blockquote>🧹 <b>𝙪𝙣𝙥𝙞𝙣 𝙖𝙡𝙡 𝙚𝙫𝙚𝙣𝙩</b> 🧹\n"
            "✦ ━━━━━━━━━━━━━━━━━━ ✦\n"
            f"👮 <b>Cleared By:</b> <a href='tg://user?id={message.from_user.id}'>{admin_name}</a>\n"
            "⚡ <b>Status:</b> Group ke sabhi pinned messages unpin kar diye gaye!</blockquote>"
        )
        await message.reply_text(text=text)
    except Exception as e:
        await message.reply_text(f"<blockquote>❌ <b>Unpinall Error:</b> <code>{e}</code></blockquote>")

# ==================== MUTE & UNMUTE ====================
@Client.on_message(filters.command("mute", prefixes=[".", "/"]) & filters.group)
async def mute_cmd(client, message):
    if not message.from_user or not await is_authorized(client, message.from_user.id, message.chat.id):
        return

    target = get_target(message)
    if not target:
        return await message.reply_text("<blockquote>⚠️ <b>Kisi user ke message par reply karke <code>.mute</code> likhein.</b></blockquote>")

    try:
        await client.restrict_chat_member(
            chat_id=message.chat.id,
            user_id=target.id,
            permissions=ChatPermissions(can_send_messages=False)
        )
        admin_name = clean_txt(message.from_user.first_name)
        target_name = clean_txt(target.first_name)

        text = (
            "<blockquote>🔇 <b>𝙢𝙪𝙩𝙚 𝙚𝙫𝙚𝙣𝙩</b> 🔇\n"
            "✦ ━━━━━━━━━━━━━━━━━━ ✦\n"
            f"👤 <b>User:</b> <a href='tg://user?id={target.id}'>{target_name}</a>\n"
            f"🆔 <b>User ID:</b> <code>{target.id}</code>\n"
            f"👮 <b>Muted By:</b> <a href='tg://user?id={message.from_user.id}'>{admin_name}</a>\n"
            "⚡ <b>Status:</b> Muted indefinitely!</blockquote>"
        )

        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔊 Unmute User", callback_data=f"unmute_{target.id}_{message.from_user.id}")]
        ])

        await message.reply_text(text=text, reply_markup=keyboard)
    except Exception as e:
        await message.reply_text(f"<blockquote>❌ <b>Mute error:</b> <code>{e}</code></blockquote>")

@Client.on_message(filters.command("unmute", prefixes=[".", "/"]) & filters.group)
async def unmute_cmd(client, message):
    if not message.from_user or not await is_authorized(client, message.from_user.id, message.chat.id):
        return

    target = get_target(message)
    if not target:
        return await message.reply_text("<blockquote>⚠️ <b>Kisi user ke message par reply karke <code>.unmute</code> likhein.</b></blockquote>")

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
            "<blockquote>🔊 <b>𝙪𝙣𝙢𝙪𝙩𝙚 𝙚𝙫𝙚𝙣𝙩</b> 🔊\n"
            "✦ ━━━━━━━━━━━━━━━━━━ ✦\n"
            f"👤 <b>User:</b> <a href='tg://user?id={target.id}'>{target_name}</a>\n"
            f"🆔 <b>User ID:</b> <code>{target.id}</code>\n"
            f"👮 <b>Unmuted By:</b> <a href='tg://user?id={message.from_user.id}'>{admin_name}</a>\n"
            "⚡ <b>Status:</b> Successfully Unmuted!</blockquote>"
        )
        await message.reply_text(text=text)
    except Exception as e:
        await message.reply_text(f"<blockquote>❌ <b>Unmute error:</b> <code>{e}</code></blockquote>")

# ==================== BAN & KICK ====================
@Client.on_message(filters.command("ban", prefixes=[".", "/"]) & filters.group)
async def ban_cmd(client, message):
    if not message.from_user or not await is_authorized(client, message.from_user.id, message.chat.id):
        return
    target = get_target(message)
    if not target:
        return await message.reply_text("<blockquote>⚠️ <b>Kisi user ke message par reply karke <code>.ban</code> likhein.</b></blockquote>")
    try:
        await client.ban_chat_member(message.chat.id, target.id)
        target_name = clean_txt(target.first_name)
        await message.reply_text(f"<blockquote>🚫 <a href='tg://user?id={target.id}'>{target_name}</a> ko permanently <b>BAN</b> kar diya gaya!</blockquote>")
    except Exception as e:
        await message.reply_text(f"<blockquote>❌ <b>Ban error:</b> <code>{e}</code></blockquote>")

@Client.on_message(filters.command("kick", prefixes=[".", "/"]) & filters.group)
async def kick_cmd(client, message):
    if not message.from_user or not await is_authorized(client, message.from_user.id, message.chat.id):
        return
    target = get_target(message)
    if not target:
        return await message.reply_text("<blockquote>⚠️ <b>Kisi user ke message par reply karke <code>.kick</code> likhein.</b></blockquote>")
    try:
        await client.ban_chat_member(message.chat.id, target.id)
        await client.unban_chat_member(message.chat.id, target.id)
        target_name = clean_txt(target.first_name)
        await message.reply_text(f"<blockquote>👢 <a href='tg://user?id={target.id}'>{target_name}</a> ko <b>KICK</b> kar diya gaya!</blockquote>")
    except Exception as e:
        await message.reply_text(f"<blockquote>❌ <b>Kick error:</b> <code>{e}</code></blockquote>")

# ==================== BUTTON CALLBACKS ====================
@Client.on_callback_query(filters.regex(r"^(demote|unmute|mute|unpinmsg)_(\d+)_(\d+)$"))
async def admin_buttons_callback(client, query: CallbackQuery):
    action, target_id, by_user_id = query.data.split("_")
    target_id = int(target_id)
    by_user_id = int(by_user_id)
    caller_id = query.from_user.id

    if caller_id != by_user_id and caller_id != ITACHI_ID:
        return await query.answer("❌ Yeh button sirf command dene wale Admin ke liye hai!", show_alert=True)

    caller_name = clean_txt(query.from_user.first_name)

    if action == "unpinmsg":
        try:
            await client.unpin_chat_message(chat_id=query.message.chat.id, message_id=target_id)
            updated_text = (
                "<blockquote>📍 <b>𝙪𝙣𝙥𝙞𝙣 𝙚𝙫𝙚𝙣𝙩</b> 📍\n"
                "✦ ━━━━━━━━━━━━━━━━━━ ✦\n"
                f"👮 <b>Unpinned By:</b> <a href='tg://user?id={caller_id}'>{caller_name}</a>\n"
                "⚡ <b>Status:</b> Message Unpinned via Quick Button!</blockquote>"
            )
            await query.message.edit_text(text=updated_text, reply_markup=None)
            await query.answer("✅ Message unpinned!")
        except Exception as e:
            await query.answer(f"Unpin failed: {e}", show_alert=True)

    elif action == "demote":
        try:
            target_user = await client.get_users(target_id)
            target_name = clean_txt(target_user.first_name)
        except Exception:
            target_name = "User"

        try:
            await client.promote_chat_member(
                chat_id=query.message.chat.id,
                user_id=target_id,
                privileges=DEMOTE_PRIVILEGES
            )
            updated_text = (
                "<blockquote>📉 <b>𝙙𝙚𝙢𝙤𝙩𝙚 𝙚𝙫𝙚𝙣𝙩</b> 📉\n"
                "✦ ━━━━━━━━━━━━━━━━━━ ✦\n"
                f"👤 <b>User:</b> <a href='tg://user?id={target_id}'>{target_name}</a>\n"
                f"🆔 <b>User ID:</b> <code>{target_id}</code>\n"
                f"👮 <b>Demoted By:</b> <a href='tg://user?id={caller_id}'>{caller_name}</a>\n"
                "⚡ <b>Status:</b> Demoted via Quick Button!</blockquote>"
            )
            await query.message.edit_text(text=updated_text, reply_markup=None)
            await query.answer("✅ User ko demote kar diya gaya!")
        except Exception as e:
            await query.answer(f"Demote failed: {e}", show_alert=True)

    elif action == "unmute":
        try:
            target_user = await client.get_users(target_id)
            target_name = clean_txt(target_user.first_name)
        except Exception:
            target_name = "User"

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
                "<blockquote>🔊 <b>𝙪𝙣𝙢𝙪𝙩𝙚 𝙚𝙫𝙚𝙣𝙩</b> 🔊\n"
                "✦ ━━━━━━━━━━━━━━━━━━ ✦\n"
                f"👤 <b>User:</b> <a href='tg://user?id={target_id}'>{target_name}</a>\n"
                f"🆔 <b>User ID:</b> <code>{target_id}</code>\n"
                f"👮 <b>Unmuted By:</b> <a href='tg://user?id={caller_id}'>{caller_name}</a>\n"
                "⚡ <b>Status:</b> Unmuted via Quick Button!</blockquote>"
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
            target_user = await client.get_users(target_id)
            target_name = clean_txt(target_user.first_name)
        except Exception:
            target_name = "User"

        try:
            await client.restrict_chat_member(
                chat_id=query.message.chat.id,
                user_id=target_id,
                permissions=ChatPermissions(can_send_messages=False)
            )
            updated_text = (
                "<blockquote>🔇 <b>𝙢𝙪𝙩𝙚 𝙚𝙫𝙚𝙣𝙩</b> 🔇\n"
                "✦ ━━━━━━━━━━━━━━━━━━ ✦\n"
                f"👤 <b>User:</b> <a href='tg://user?id={target_id}'>{target_name}</a>\n"
                f"🆔 <b>User ID:</b> <code>{target_id}</code>\n"
                f"👮 <b>Muted By:</b> <a href='tg://user?id={caller_id}'>{caller_name}</a>\n"
                "⚡ <b>Status:</b> Muted via Quick Button!</blockquote>"
            )
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("🔊 Unmute User", callback_data=f"unmute_{target_id}_{caller_id}")]
            ])
            await query.message.edit_text(text=updated_text, reply_markup=keyboard)
            await query.answer("✅ User ko wapas mute kar diya gaya!")
        except Exception as e:
            await query.answer(f"Mute failed: {e}", show_alert=True)
            
