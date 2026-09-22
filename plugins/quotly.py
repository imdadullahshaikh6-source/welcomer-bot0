import io
import aiohttp
from pyrogram import Client, filters
from pyrogram.types import Message

QUOTLY_API = "https://quote.yuri.ly/generate"

@Client.on_message(filters.command(["q", "quote"], prefixes=[".", "/"]) & filters.group)
async def quotly_maker(client: Client, message: Message):
    # Check karein ki message kisi par reply hai ya nahi
    reply = message.reply_to_message
    if not reply:
        return await message.reply_text("> ⚠️ **Kisi user ke message par reply karke `.q` likhein.**")

    # Text check
    text = reply.text or reply.caption
    if not text:
        return await message.reply_text("> ⚠️ **Sirf text messages ko quote sticker banaya ja sakta hai.**")

    status_msg = await message.reply_text("> 🔄 **Sticker ban raha hai, thoda intezar karein...**")

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

    # Message payload tayar karein
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

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(QUOTLY_API, json=payload) as resp:
                if resp.status != 200:
                    await status_msg.edit_text("> ❌ **Sticker create karne mein dikkat aayi. Kripya baad mein prayas karein.**")
                    return
                
                sticker_bytes = await resp.read()

        # Sticker ko memory buffer mein load karein
        sticker_file = io.BytesIO(sticker_bytes)
        sticker_file.name = "quote.webp"

        # Group mein sticker send karein
        await client.send_sticker(
            chat_id=message.chat.id,
            sticker=sticker_file,
            reply_to_message_id=reply.id
        )
        await status_msg.delete()

    except Exception as e:
        await status_msg.edit_text(f"> ❌ **Error:** `{e}`")
      
