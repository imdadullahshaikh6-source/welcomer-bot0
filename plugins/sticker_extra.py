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
        return None

    try:
        res_json = json.loads(raw_response.decode("utf-8"))
        if not res_json.get("ok"):
            return None

        image_bytes = base64.b64decode(res_json["result"]["image"])
        img = Image.open(io.BytesIO(image_bytes))
        img.thumbnail((512, 512))

        bio = io.BytesIO()
        bio.name = "sticker.webp"
        img.save(bio, format="WEBP")
        bio.seek(0)
        return bio
    except Exception:
        return None


# ==================== .qr (QUOTE REPLY) ==================== #
@Client.on_message(filters.command(["qr"], prefixes=[".", "/", "!"]))
async def quote_reply_cmd(client: Client, message: Message):
    reply = message.reply_to_message
    if not reply:
        return await message.reply_text("<blockquote>⚠️ <b>Kisi message par reply karke .qr use karein!</b></blockquote>")

    text = reply.text or reply.caption
    if not text or not str(text).strip():
        return await message.reply_text("<blockquote>⚠️ <b>Sirf text message ka quote ban sakta hai!</b></blockquote>")

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

    msg_obj = {
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

    if reply.reply_to_message:
        rep2 = reply.reply_to_message
        rep2_user = rep2.from_user
        r_name = rep2_user.first_name if rep2_user else (rep2.sender_chat.title if rep2.sender_chat else "User")
        r_text = rep2.text or rep2.caption or "Media"
        msg_obj["replyMessage"] = {
            "name": r_name,
            "text": str(r_text),
            "chatId": rep2.chat.id
        }

    payload = {
        "type": "quote",
        "format": "webp",
        "backgroundColor": "#1b1429",
        "width": 512,
        "height": 512,
        "scale": 2,
        "messages": [msg_obj]
    }

    try:
        sticker_file = await client.loop.run_in_executor(None, generate_quotly_sticker, payload)
        if not sticker_file:
            return await message.reply_text("<blockquote>❌ <b>Quote API response nahi de rahi!</b></blockquote>")

        await client.send_sticker(
            chat_id=message.chat.id,
            sticker=sticker_file,
            reply_to_message_id=reply.id
        )
    except Exception as e:
        await message.reply_text(f"<blockquote>❌ <b>Error:</b> {e}</blockquote>")
        
