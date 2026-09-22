import io
import json
import base64
import urllib.request
from PIL import Image
from pyrogram import Client, filters
from pyrogram.types import Message

QUOTLY_ENDPOINTS = [
    "https://quote.antispam.bot/generate",
    "https://quotly.herokuapp.com/generate",
    "https://quote.yuri.ly/generate"
]

def generate_quotly_sticker(payload: dict) -> io.BytesIO:
    data = json.dumps(payload).encode("utf-8")
    raw_response = None

    # Working endpoint se fetch karein
    for url in QUOTLY_ENDPOINTS:
        try:
            req = urllib.request.Request(
                url,
                data=data,
                headers={
                    "Content-Type": "application/json",
                    "User-Agent": "Mozilla/5.0"
                }
            )
            with urllib.request.urlopen(req, timeout=10) as resp:
                if resp.status == 200:
                    raw_response = resp.read()
                    break
        except Exception:
            continue

    if not raw_response:
        raise Exception("Quotly server filhaal respond nahi kar raha hai.")

    # Check karein agar response JSON format me base64 hai
    image_bytes = None
    try:
        res_json = json.loads(raw_response.decode("utf-8"))
        if "result" in res_json and "image" in res_json["result"]:
            image_bytes = base64.b64decode(res_json["result"]["image"])
    except Exception:
        # Direct binary image response
        image_bytes = raw_response

    if not image_bytes:
        raise Exception("Invalid image data received.")

    # Pillow ke sath proper 512x512 Telegram sticker format me compress karein
    img = Image.open(io.BytesIO(image_bytes))
    img.thumbnail((512, 512))

    bio = io.BytesIO()
    bio.name = "sticker.webp"
    img.save(bio, format="WEBP")
    bio.seek(0)
    return bio

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
        sticker_file = await client.loop.run_in_executor(None, generate_quotly_sticker, payload)

        await client.send_sticker(
            chat_id=message.chat.id,
            sticker=sticker_file,
            reply_to_message_id=reply.id
        )
    except Exception as e:
        await message.reply_text(f"<blockquote>❌ <b>Error:</b> <code>{e}</code></blockquote>")
        
