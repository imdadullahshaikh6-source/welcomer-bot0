import os
import aiohttp
from pyrogram import Client, filters
from pyrogram.types import Message

QUOTLY_API = "https://quote.yuri.ly/generate"

@Client.on_message(filters.command(["q", "quote"], prefixes=[".", "/"]) & filters.group)
async def quotly_maker(client: Client, message: Message):
    reply = message.reply_to_message
    if not reply:
        return await message.reply_text("<blockquote>⚠️ <b>Kisi ke message par reply karke <code>.q</code> likhein.</b></blockquote>")

    text = reply.text or reply.caption
    if not text:
        return await message.reply_text("<blockquote>⚠️ <b>Sirf text message ka quote sticker ban sakta hai.</b></blockquote>")

    user = reply.from_user
    if user:
        first_name = user.first_name or "User"
        last_name = user.last_name or ""
        user_id = user.id
        username = user.username or ""
    else:
        first_name = reply.sender_chat.title if reply.sender_chat else "Anonymous"
        last_name = ""
        user_id = reply.sender_chat.id if reply.sender_chat else 1000
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
                "text": text
            }
        ]
    }

    temp_sticker_path = f"sticker_{message.id}.webp"

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(QUOTLY_API, json=payload, timeout=aiohttp.ClientTimeout(total=20)) as resp:
                if resp.status != 200:
                    return await message.reply_text("<blockquote>❌ <b>Quotly server se sticker generate nahi ho paya.</b></blockquote>")
                sticker_data = await resp.read()

        # Local storage me temporarily write karein
        with open(temp_sticker_path, "wb") as f:
            f.write(sticker_data)

        # Local path se send karne par Telegram isko strictly "Sticker" hi render karega
        await client.send_sticker(
            chat_id=message.chat.id,
            sticker=temp_sticker_path,
            reply_to_message_id=reply.id
        )

    except Exception as e:
        await message.reply_text(f"<blockquote>❌ <b>Error:</b> <code>{e}</code></blockquote>")
    finally:
        # File delete karke space clean karein
        if os.path.exists(temp_sticker_path):
            os.remove(temp_sticker_path)
            
