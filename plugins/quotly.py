import io
import aiohttp
from pyrogram import Client, filters
from pyrogram.types import Message

QUOTLY_API = "https://quote.yuri.ly/generate"

@Client.on_message(filters.command(["q", "quote"], prefixes=[".", "/"]) & filters.group)
async def quotly_maker(client: Client, message: Message):
    reply = message.reply_to_message
    if not reply:
        return await message.reply_text("<blockquote>⚠️ <b>Kisi ke text message par reply karke <code>.q</code> likhein.</b></blockquote>")

    text = reply.text or reply.caption
    if not text or not str(text).strip():
        return await message.reply_text("<blockquote>⚠️ <b>Sirf text message ka sticker ban sakta hai.</b></blockquote>")

    user = reply.from_user
    if user:
        first_name = user.first_name or "User"
        last_name = user.last_name or ""
        user_id = user.id
        username = user.username or ""
    elif reply.sender_chat:
        first_name = reply.sender_chat.title or "Anonymous"
        last_name = ""
        user_id = reply.sender_chat.id
        username = reply.sender_chat.username or ""
    else:
        first_name = "User"
        last_name = ""
        user_id = 1000
        username = ""

    # Telegram stickers ke liye 512x512 box zaroori hota hai
    payload = {
        "type": "quote",
        "format": "webp",
        "backgroundColor": "#1b1429",
        "width": 512,
        "height": 512,
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
                "text": str(text)
            }
        ]
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(QUOTLY_API, json=payload, timeout=aiohttp.ClientTimeout(total=15)) as resp:
                if resp.status != 200:
                    return await message.reply_text("<blockquote>❌ <b>Quotly server abhi busy hai, baad mein prayas karein.</b></blockquote>")
                sticker_bytes = await resp.read()

        sticker_bio = io.BytesIO(sticker_bytes)
        sticker_bio.name = "sticker.webp"
        sticker_bio.seek(0)

        await client.send_sticker(
            chat_id=message.chat.id,
            sticker=sticker_bio,
            reply_to_message_id=reply.id
        )
    except Exception as e:
        await message.reply_text(f"<blockquote>❌ <b>Error:</b> <code>{e}</code></blockquote>")
        
