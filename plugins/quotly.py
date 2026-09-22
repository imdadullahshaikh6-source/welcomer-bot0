import os
import aiohttp
from pyrogram import Client, filters
from pyrogram.types import Message

BOT_TOKEN = os.environ.get("BOT_TOKEN")
QUOTLY_API = "https://quote.yuri.ly/generate"

@Client.on_message(filters.command(["q", "quote"], prefixes=[".", "/"]) & filters.group)
async def quotly_maker(client: Client, message: Message):
    reply = message.reply_to_message
    if not reply:
        return await message.reply_text("<blockquote>⚠️ <b>Kisi ke message par reply karke <code>.q</code> likhein.</b></blockquote>")

    msg_text = str(reply.text or reply.caption or "").strip()
    if not msg_text:
        return await message.reply_text("<blockquote>⚠️ <b>Sirf text message ka quote sticker ban sakta hai.</b></blockquote>")

    user = reply.from_user
    if user:
        first_name = str(user.first_name) if user.first_name else "User"
        last_name = str(user.last_name) if user.last_name else ""
        user_id = int(user.id)
        username = str(user.username) if user.username else ""
    elif reply.sender_chat:
        first_name = str(reply.sender_chat.title) if reply.sender_chat.title else "Anonymous"
        last_name = ""
        user_id = int(reply.sender_chat.id)
        username = str(reply.sender_chat.username) if reply.sender_chat.username else ""
    else:
        first_name = "User"
        last_name = ""
        user_id = 1000
        username = ""

    payload = {
        "type": "quote",
        "format": "webp",
        "backgroundColor": "#1b1429",
        "width": 512,
        "height": 768,
        "scale": 2,
        "messages": [
            {
                "entities": [],
                "avatar": True,
                "from": {
                    "id": user_id,
                    "first_name": first_name,
                    "last_name": last_name,
                    "username": username
                },
                "text": msg_text
            }
        ]
    }

    try:
        async with aiohttp.ClientSession() as session:
            # 1. Quotly API se sticker download karein
            async with session.post(QUOTLY_API, json=payload, timeout=aiohttp.ClientTimeout(total=20)) as resp:
                if resp.status != 200:
                    return await message.reply_text("<blockquote>❌ <b>Quotly server busy hai, thodi der baad try karein.</b></blockquote>")
                sticker_bytes = await resp.read()

            # 2. Telegram Bot API sendSticker method ko directly raw multipart me send karein
            telegram_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendSticker"
            form = aiohttp.FormData()
            form.add_field("chat_id", str(message.chat.id))
            form.add_field("reply_to_message_id", str(reply.id))
            form.add_field(
                "sticker",
                sticker_bytes,
                filename="sticker.webp",
                content_type="image/webp"
            )

            async with session.post(telegram_url, data=form) as tg_resp:
                if tg_resp.status != 200:
                    err_json = await tg_resp.json()
                    await message.reply_text(f"<blockquote>❌ <b>Telegram Error:</b> <code>{err_json}</code></blockquote>")

    except Exception as e:
        await message.reply_text(f"<blockquote>❌ <b>Error:</b> <code>{e}</code></blockquote>")
        
