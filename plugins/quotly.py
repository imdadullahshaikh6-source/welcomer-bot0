import io
import json
import urllib.request
from PIL import Image
from pyrogram import Client, filters
from pyrogram.types import Message

QUOTLY_URL = "https://quote.yuri.ly/generate"

def generate_quotly(payload: dict) -> io.BytesIO:
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        QUOTLY_URL,
        data=data,
        headers={
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0"
        }
    )
    with urllib.request.urlopen(req, timeout=15) as response:
        raw_bytes = response.read()

    # Image ko Telegram sticker dimensions (max 512x512) ke according strictly format karein
    img = Image.open(io.BytesIO(raw_bytes))
    img.thumbnail((512, 512))

    sticker_bio = io.BytesIO()
    sticker_bio.name = "sticker.webp"
    img.save(sticker_bio, format="WEBP")
    sticker_bio.seek(0)
    return sticker_bio

@Client.on_message(filters.command(["q", "quote"], prefixes=[".", "/"]) & filters.group)
async def quotly_cmd(client: Client, message: Message):
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
        sticker_bio = await client.loop.run_in_executor(None, generate_quotly, payload)

        await client.send_sticker(
            chat_id=message.chat.id,
            sticker=sticker_bio,
            reply_to_message_id=reply.id
        )
    except Exception as e:
        await message.reply_text(f"<blockquote>❌ <b>Error:</b> <code>{e}</code></blockquote>")
        
