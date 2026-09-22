import os
import json
import asyncio
import urllib.request
import re
from pyrogram import Client, filters
from pyrogram.types import ChatPrivileges, ChatPermissions, CallbackQuery, Message

BOT_TOKEN = os.environ.get("BOT_TOKEN", "").strip().strip('"').strip("'")

DEMOTE_PRIVILEGES = ChatPrivileges(
    can_manage_chat=False,
    can_delete_messages=False,
    can_restrict_members=False,
    can_invite_users=False,
    can_pin_messages=False,
    can_manage_video_chats=False,
    can_promote_members=False
)

async def call_tg_bot_api(endpoint: str, payload: dict):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/{endpoint}"
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})

    def _sync():
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except Exception:
            return None

    return await asyncio.to_thread(_sync)

async def is_admin(client: Client, user_id: int, chat_id: int) -> bool:
    try:
        member = await client.get_chat_member(chat_id, user_id)
        return member.status.name in ["OWNER", "ADMINISTRATOR"]
    except Exception:
        return False

def get_target(message: Message):
    if message.reply_to_message and message.reply_to_message.from_user:
        return message.reply_to_message.from_user
    return None

def clean_txt(text: str) -> str:
    return re.sub(r'[*_`\[\]()<>]', '', text or "User")

# ==================== PROMOTE & DEMOTE ====================
@Client.on_message(filters.command("promote", prefixes=[".", "/"]) & filters.group)
async def promote_cmd(client: Client, message: Message):
    if not message.from_user or not await is_admin(client, message.from_user.id, message.chat.id):
        return

    target = get_target(message)
    if not target:
        return await message.reply_text("<blockquote>⚠️ <b>Kisi ke message par reply karke <code>.promote</code> likhein.</b></blockquote>")

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

        text = (
            "<blockquote>✨ <b>𝙥𝙧𝙤𝙢𝙤𝙩𝙚 𝙚𝙫𝙚𝙣𝙩</b> ✨\n"
            "✦ ━━━━━━━━━━━━━━━━━━ ✦\n"
            f"👤 <b>User:</b> <a href='tg://user?id={target.id}'>{clean_txt(target.first_name)}</a>\n"
            f"🏷️ <b>Title:</b> <code>{title}</code>\n"
            f"👑 <b>By:</b> <a href='tg://user?id={message.from_user.id}'>{clean_txt(message.from_user.first_name)}</a></blockquote>"
        )
        markup = {
            "inline_keyboard": [
                [{"text": "🔴 Demote User", "callback_data": f"demote_{target.id}", "style": "danger"}]
            ]
        }
        await call_tg_bot_api("sendMessage", {
            "chat_id": message.chat.id,
            "text": text,
            "parse_mode": "HTML",
            "reply_markup": markup
        })
    except Exception as e:
        await message.reply_text(f"<blockquote>❌ <b>Error:</b> <code>{e}</code></blockquote>")

@Client.on_message(filters.command("demote", prefixes=[".", "/"]) & filters.group)
async def demote_cmd(client: Client, message: Message):
    if not message.from_user or not await is_admin(client, message.from_user.id, message.chat.id):
        return

    target = get_target(message)
    if not target:
        return await message.reply_text("<blockquote>⚠️ <b>Kisi admin ke message par reply karke <code>.demote</code> likhein.</b></blockquote>")

    try:
        await client.promote_chat_member(chat_id=message.chat.id, user_id=target.id, privileges=DEMOTE_PRIVILEGES)
        text = (
            "<blockquote>📉 <b>𝙙𝙚𝙢𝙤𝙩𝙚 𝙚𝙫𝙚𝙣𝙩</b> 📉\n"
            "✦ ━━━━━━━━━━━━━━━━━━ ✦\n"
            f"👤 <b>User:</b> <a href='tg://user?id={target.id}'>{clean_txt(target.first_name)}</a>\n"
            f"👮 <b>Demoted By:</b> <a href='tg://user?id={message.from_user.id}'>{clean_txt(message.from_user.first_name)}</a></blockquote>"
        )
        await message.reply_text(text=text)
    except Exception as e:
        await message.reply_text(f"<blockquote>❌ <b>Error:</b> <code>{e}</code></blockquote>")

# ==================== PIN & UNPIN ====================
@Client.on_message(filters.command("pin", prefixes=[".", "/"]) & filters.group)
async def pin_cmd(client: Client, message: Message):
    if not message.from_user or not await is_admin(client, message.from_user.id, message.chat.id):
        return

    if not message.reply_to_message:
        return await message.reply_text("<blockquote>⚠️ <b>Kisi message par reply karke <code>.pin</code> likhein.</b></blockquote>")

    disable_notification = True
    if len(message.command) > 1 and message.command[1].lower() in ["loud", "notify"]:
        disable_notification = False

    try:
        await client.pin_chat_message(
            chat_id=message.chat.id,
            message_id=message.reply_to_message.id,
            disable_notification=disable_notification
        )
        text = (
            "<blockquote>📌 <b>𝙥𝙞𝙣 𝙚𝙫𝙚𝙣𝙩</b> 📌\n"
            "✦ ━━━━━━━━━━━━━━━━━━ ✦\n"
            f"👮 <b>By:</b> <a href='tg://user?id={message.from_user.id}'>{clean_txt(message.from_user.first_name)}</a></blockquote>"
        )
        markup = {
            "inline_keyboard": [
                [{"text": "🔴 Unpin Message", "callback_data": f"unpinmsg_{message.reply_to_message.id}", "style": "danger"}]
            ]
        }
        await call_tg_bot_api("sendMessage", {
            "chat_id": message.chat.id,
            "text": text,
            "parse_mode": "HTML",
            "reply_markup": markup
        })
    except Exception as e:
        await message.reply_text(f"<blockquote>❌ <b>Error:</b> <code>{e}</code></blockquote>")

@Client.on_message(filters.command("unpin", prefixes=[".", "/"]) & filters.group)
async def unpin_cmd(client: Client, message: Message):
    if not message.from_user or not await is_admin(client, message.from_user.id, message.chat.id):
        return
    if not message.reply_to_message:
        return await message.reply_text("<blockquote>⚠️ <b>Kisi pinned message par reply karein.</b></blockquote>")
    try:
        await client.unpin_chat_message(chat_id=message.chat.id, message_id=message.reply_to_message.id)
        await message.reply_text("<blockquote>📍 <b>Message unpinned!</b></blockquote>")
    except Exception as e:
        await message.reply_text(f"<blockquote>❌ <b>Error:</b> <code>{e}</code></blockquote>")

@Client.on_message(filters.command("unpinall", prefixes=[".", "/"]) & filters.group)
async def unpinall_cmd(client: Client, message: Message):
    if not message.from_user or not await is_admin(client, message.from_user.id, message.chat.id):
        return
    try:
        await client.unpin_all_chat_messages(chat_id=message.chat.id)
        await message.reply_text("<blockquote>🧹 <b>Group ke saare pinned messages unpin kar diye gaye!</b></blockquote>")
    except Exception as e:
        await message.reply_text(f"<blockquote>❌ <b>Error:</b> <code>{e}</code></blockquote>")

# ==================== MUTE & UNMUTE ====================
@Client.on_message(filters.command("mute", prefixes=[".", "/"]) & filters.group)
async def mute_cmd(client: Client, message: Message):
    if not message.from_user or not await is_admin(client, message.from_user.id, message.chat.id):
        return

    target = get_target(message)
    if not target:
        return await message.reply_text("<blockquote>⚠️ <b>Kisi user ke message par reply karein.</b></blockquote>")

    try:
        await client.restrict_chat_member(
            chat_id=message.chat.id,
            user_id=target.id,
            permissions=ChatPermissions(can_send_messages=False)
        )
        text = (
            "<blockquote>🔇 <b>𝙢𝙪𝙩𝙚 𝙚𝙫𝙚𝙣𝙩</b> 🔇\n"
            "✦ ━━━━━━━━━━━━━━━━━━ ✦\n"
            f"👤 <b>User:</b> <a href='tg://user?id={target.id}'>{clean_txt(target.first_name)}</a>\n"
            f"👮 <b>By:</b> <a href='tg://user?id={message.from_user.id}'>{clean_txt(message.from_user.first_name)}</a></blockquote>"
        )
        markup = {
            "inline_keyboard": [
                [{"text": "🟢 Unmute User", "callback_data": f"unmute_{target.id}", "style": "success"}]
            ]
        }
        await call_tg_bot_api("sendMessage", {
            "chat_id": message.chat.id,
            "text": text,
            "parse_mode": "HTML",
            "reply_markup": markup
        })
    except Exception as e:
        await message.reply_text(f"<blockquote>❌ <b>Error:</b> <code>{e}</code></blockquote>")

@Client.on_message(filters.command("unmute", prefixes=[".", "/"]) & filters.group)
async def unmute_cmd(client: Client, message: Message):
    if not message.from_user or not await is_admin(client, message.from_user.id, message.chat.id):
        return

    target = get_target(message)
    if not target:
        return await message.reply_text("<blockquote>⚠️ <b>Kisi user ke message par reply karein.</b></blockquote>")

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
        await message.reply_text(f"<blockquote>🔊 <a href='tg://user?id={target.id}'>{clean_txt(target.first_name)}</a> is unmuted!</blockquote>")
    except Exception as e:
        await message.reply_text(f"<blockquote>❌ <b>Error:</b> <code>{e}</code></blockquote>")

# ==================== BAN & KICK ====================
@Client.on_message(filters.command("ban", prefixes=[".", "/"]) & filters.group)
async def ban_cmd(client: Client, message: Message):
    if not message.from_user or not await is_admin(client, message.from_user.id, message.chat.id):
        return
    target = get_target(message)
    if not target:
        return await message.reply_text("<blockquote>⚠️ <b>Kisi user ke message par reply karein.</b></blockquote>")
    try:
        await client.ban_chat_member(message.chat.id, target.id)
        await message.reply_text(f"<blockquote>🚫 <a href='tg://user?id={target.id}'>{clean_txt(target.first_name)}</a> banned!</blockquote>")
    except Exception as e:
        await message.reply_text(f"<blockquote>❌ <b>Error:</b> <code>{e}</code></blockquote>")

@Client.on_message(filters.command("kick", prefixes=[".", "/"]) & filters.group)
async def kick_cmd(client: Client, message: Message):
    if not message.from_user or not await is_admin(client, message.from_user.id, message.chat.id):
        return
    target = get_target(message)
    if not target:
        return await message.reply_text("<blockquote>⚠️ <b>Kisi user ke message par reply karein.</b></blockquote>")
    try:
        await client.ban_chat_member(message.chat.id, target.id)
        await client.unban_chat_member(message.chat.id, target.id)
        await message.reply_text(f"<blockquote>👢 <a href='tg://user?id={target.id}'>{clean_txt(target.first_name)}</a> kicked!</blockquote>")
    except Exception as e:
        await message.reply_text(f"<blockquote>❌ <b>Error:</b> <code>{e}</code></blockquote>")

# ==================== BUTTON CALLBACKS ====================
@Client.on_callback_query(filters.regex(r"^(demote|unmute|unpinmsg)_(\d+)$"))
async def admin_buttons_callback(client: Client, query: CallbackQuery):
    action, target_id = query.data.split("_")
    target_id = int(target_id)
    caller_id = query.from_user.id

    if not await is_admin(client, caller_id, query.message.chat.id):
        return await query.answer("❌ Sirf Group Admins ke liye!", show_alert=True)

    if action == "unpinmsg":
        try:
            await client.unpin_chat_message(chat_id=query.message.chat.id, message_id=target_id)
            await call_tg_bot_api("editMessageText", {
                "chat_id": query.message.chat.id,
                "message_id": query.message.id,
                "text": "<blockquote>📍 <b>Message unpinned via quick button!</b></blockquote>",
                "parse_mode": "HTML"
            })
            await query.answer("✅ Unpinned!")
        except Exception as e:
            await query.answer(f"Failed: {e}", show_alert=True)

    elif action == "demote":
        try:
            await client.promote_chat_member(chat_id=query.message.chat.id, user_id=target_id, privileges=DEMOTE_PRIVILEGES)
            await call_tg_bot_api("editMessageText", {
                "chat_id": query.message.chat.id,
                "message_id": query.message.id,
                "text": "<blockquote>📉 <b>User demoted via quick button!</b></blockquote>",
                "parse_mode": "HTML"
            })
            await query.answer("✅ Demoted!")
        except Exception as e:
            await query.answer(f"Failed: {e}", show_alert=True)

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
            await call_tg_bot_api("editMessageText", {
                "chat_id": query.message.chat.id,
                "message_id": query.message.id,
                "text": "<blockquote>🔊 <b>User unmuted via quick button!</b></blockquote>",
                "parse_mode": "HTML"
            })
            await query.answer("✅ Unmuted!")
        except Exception as e:
            await query.answer(f"Failed: {e}", show_alert=True)
            
