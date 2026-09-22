import io
import base64
import aiohttp
from pyrogram import Client, filters
from pyrogram.types import Message

QUOTLY_API = "https://quote.yuri.ly/generate"

@Client.on_message(filters.command(["q", "quote"], prefixes=[".", "/"]) & filters.group)
async def quotly_maker(client: Client, message: Message):
    reply = message.reply_to_message
    if not reply:
        return await message.reply_text("<blockquote>⚠️ <b>Kisi user ke text message par reply karke <code>.q</code> likhein.</b></blockquote>")

    text = reply.text or reply.caption
    if not text:
        return await message.reply_text("<blockquote>⚠️ <b>Sirf text message ka quote sticker banaya ja sakta hai.</b></blockquote>")

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

    # User Profile Photo fetch karne ka try karein
    avatar_base64 = None
    try:
        photos = [p async for p in client.get_chat_photos(user_id, limit=1)]
        if photos:
            photo_file = await client.download_media(photos[0].file_id, in_memory=True)
            avatar_base64 = base64.b64encode(photo_file.getvalue()).decode("utf-8")
    except Exception:
        avatar_base64 = None

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

    if avatar_base64:
        payload["messages"][0]["avatar"] = avatar_base64

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(QUOTLY_API, json=payload, timeout=aiohttp.ClientTimeout(total=20)) as resp:
                if resp.status != 200:
                    return await message.reply_text("<blockquote>❌ <b>Sticker create karne mein dikkat aayi. Baad mein prayas karein.</b></blockquote>")
                sticker_bytes = await resp.read()

        sticker_io = io.BytesIO(sticker_bytes)
        sticker_io.name = "sticker.webp"
        sticker_io.seek(0)

        # Direct as sticker bhejna (document format nahi banega)
        await message.reply_sticker(sticker=sticker_io)

    except Exception as e:
        await message.reply_text(f"<blockquote>❌ <b>Error:</b> <code>{e}</code></blockquote>")
        
