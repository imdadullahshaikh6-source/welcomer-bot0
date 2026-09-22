import asyncio
from pyrogram import Client, filters
from pyrogram.enums import ParseMode
from pyrogram.types import Message
from pyrogram.errors import FloodWait

ITACHI_ID = 8373739674

# Processing state tracker
processing_chats = set()

async def is_authorized(client: Client, user_id: int, chat_id: int) -> bool:
    if user_id == ITACHI_ID:
        return True
    try:
        member = await client.get_chat_member(chat_id, user_id)
        if member.status.name in ["OWNER", "ADMINISTRATOR"]:
            return True
    except Exception:
        pass
    return False

# ==================== .uthao (Fetch & Approve Pending Requests) ====================
@Client.on_message(filters.command(["uthao"], prefixes=[".", "/"]) & filters.group)
async def uthao_pending_requests(client: Client, message: Message):
    if not message.from_user or not await is_authorized(client, message.from_user.id, message.chat.id):
        return

    chat_id = message.chat.id

    if chat_id in processing_chats:
        return await message.reply_text(
            "<blockquote>⚠️ <b>Pending requests uthane ka process pehle se hi chal raha hai!</b></blockquote>",
            parse_mode=ParseMode.HTML
        )

    processing_chats.add(chat_id)
    admin_name = message.from_user.first_name or "Admin"

    status_msg = await message.reply_text(
        "<blockquote>⚡ <b>𝙥𝙚𝙣𝙙𝙞𝙣𝙜 𝙧𝙚𝙦𝙪𝙚𝙨𝙩𝙨 𝙥𝙧𝙤𝙘𝙚𝙨𝙨</b> ⚡\n"
        "✦ ━━━━━━━━━━━━━━━━━━ ✦\n"
        f"👮 <b>Initiated By:</b> <a href='tg://user?id={message.from_user.id}'>{admin_name}</a>\n"
        "🔍 <b>Task:</b> Pending requests scan aur approve ho rahi hain...\n"
        "🛑 <i>Rokne ke liye <code>.ruko</code> likhein.</i></blockquote>",
        parse_mode=ParseMode.HTML
    )

    accepted_count = 0

    try:
        # Pending join requests fetch karein
        async for req in client.get_chat_join_requests(chat_id):
            # Check karein agar admin ne .ruko command diya ho
            if chat_id not in processing_chats:
                break

            user = req.user
            try:
                # Request approve karein
                await client.approve_chat_join_request(chat_id=chat_id, user_id=user.id)
                accepted_count += 1

                first_name = user.first_name or "New Member"
                mention = f"<a href='tg://user?id={user.id}'>{first_name}</a>"

                welcome_text = (
                    "<blockquote>✨ <b>𝙬𝙚𝙡𝙘𝙤𝙢𝙚 𝙩𝙤 𝙩𝙝𝙚 𝙛𝙖𝙢𝙞𝙡𝙮</b> ✨\n"
                    "✦ ━━━━━━━━━━━━━━━━━━ ✦\n"
                    f"👋 Hello {mention}!\n"
                    "🎉 Aapka join request accept ho gaya hai.\n"
                    "💬 Chat rules follow karein aur chill karein!</blockquote>"
                )

                await client.send_message(chat_id=chat_id, text=welcome_text, parse_mode=ParseMode.HTML)
                
                # Telegram rate-limits se bachne ke liye chhota delay
                await asyncio.sleep(1.5)

            except FloodWait as f:
                await asyncio.sleep(f.value)
            except Exception:
                pass

        if chat_id in processing_chats:
            processing_chats.remove(chat_id)

        finish_text = (
            "<blockquote>✅ <b>𝙩𝙖𝙨𝙠 𝙘𝙤𝙢𝙥𝙡𝙚𝙩𝙚𝙙</b> ✅\n"
            "✦ ━━━━━━━━━━━━━━━━━━ ✦\n"
            f"📊 <b>Total Accepted:</b> <code>{accepted_count}</code> pending users\n"
            "⚡ <b>Status:</b> Sabhi pending requests clear kar di gayi hain!</blockquote>"
        )
        await status_msg.edit_text(text=finish_text, parse_mode=ParseMode.HTML)

    except Exception as e:
        if chat_id in processing_chats:
            processing_chats.remove(chat_id)
        await status_msg.edit_text(f"<blockquote>❌ <b>Error:</b> <code>{e}</code></blockquote>", parse_mode=ParseMode.HTML)

# ==================== .ruko (Stop the Process) ====================
@Client.on_message(filters.command(["ruko"], prefixes=[".", "/"]) & filters.group)
async def ruko_pending_requests(client: Client, message: Message):
    if not message.from_user or not await is_authorized(client, message.from_user.id, message.chat.id):
        return

    chat_id = message.chat.id
    if chat_id not in processing_chats:
        return await message.reply_text(
            "<blockquote>⚠️ <b>Abhi koi request uthane ka process nahi chal raha hai!</b></blockquote>",
            parse_mode=ParseMode.HTML
        )

    # Process stop karne ka signal
    processing_chats.remove(chat_id)
    admin_name = message.from_user.first_name or "Admin"

    stop_text = (
        "<blockquote>🛑 <b>𝙥𝙧𝙤𝙘𝙚𝙨𝙨 𝙨𝙩𝙤𝙥𝙥𝙚𝙙</b> 🛑\n"
        "✦ ━━━━━━━━━━━━━━━━━━ ✦\n"
        f"👮 <b>Stopped By:</b> <a href='tg://user?id={message.from_user.id}'>{admin_name}</a>\n"
        "🔴 <b>Status:</b> Pending requests approve karna turant rok diya gaya hai.</blockquote>"
    )
    await message.reply_text(text=stop_text, parse_mode=ParseMode.HTML)
    
