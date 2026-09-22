import io
import aiohttp
from pyrogram import Client, filters
from pyrogram.types import Message

QUOTLY_API = "https://quote.yuri.ly/generate"

@Client.on_message(filters.command(["q", "quote"], prefixes=[".", "/"]) & filters.group)
async def quotly_maker(client: Client, message: Message):
    reply = message.reply_to_message
    if not reply:
        return await message.reply_text("<blockquote>⚠️ <b>Kisi ke message par reply karke <code>.q</code> likhein.</b></blockquote>")

    # Safely text extract karein (string guarantee ke sath)
    msg_text = ""
    if reply.text:
        msg_text = str(reply.text)
    elif reply.caption:
        msg_text = str(reply.caption)

    if not msg_text.strip():
        return await message.reply_text("<blockquote>⚠️ <b>Sirf text message ka quote sticker banaya ja sakta hai.</b></blockquote>")

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
            async with session.post(QUOTLY_API, json=payload, timeout=aiohttp.ClientTimeout(total=20)) as resp:
                if resp.status != 200:
                    return await message.reply_text("<blockquote>❌ <b>Sticker banne me dikkat aayi. Baad me prayas karein.</b></blockquote>")
                sticker_bytes = await resp.read()

        sticker_file = io.BytesIO(sticker_bytes)
        sticker_file.name = "sticker.webp"

        # Reply to original quoted message directly
        await client.send_sticker(
            chat_id=message.chat.id,
            sticker=sticker_file,
            reply_to_message_id=reply.id
        )

    except Exception as e:
        await message.reply_text(f"<blockquote>❌ <b>Error:</b> <code>{e}</code></blockquote>")
        
