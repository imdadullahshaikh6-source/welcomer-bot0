import io
import os
import json
import base64
import urllib.request
import urllib.parse
from PIL import Image

from pyrogram import Client, filters
from pyrogram.types import Message

# Database collection import
try:
    from database import db
    kang_db = db.kang_packs
except Exception:
    kang_db = None

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


# ==================== .kang (STICKER KANG + MONGO SAVE) ==================== #
def call_bot_api(token: str, method: str, data: dict = None, files: dict = None):
    boundary = "----WebKitFormBoundary7MA4YWxkTrZu0gW"
    url = f"https://api.telegram.org/bot{token}/{method}"
    
    body = bytearray()
    if data:
        for k, v in data.items():
            body.extend(f"--{boundary}\r\n".encode())
            body.extend(f'Content-Disposition: form-data; name="{k}"\r\n\r\n'.encode())
            body.extend(f"{v}\r\n".encode())
            
    if files:
        for k, (filename, filedata, mtype) in files.items():
            body.extend(f"--{boundary}\r\n".encode())
            body.extend(f'Content-Disposition: form-data; name="{k}"; filename="{filename}"\r\n'.encode())
            body.extend(f"Content-Type: {mtype}\r\n\r\n".encode())
            body.extend(filedata)
            body.extend(b"\r\n")
            
    body.extend(f"--{boundary}--\r\n".encode())
    
    req = urllib.request.Request(
        url,
        data=bytes(body),
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"}
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        return json.loads(e.read().decode())
    except Exception as e:
        return {"ok": False, "description": str(e)}


@Client.on_message(filters.command(["kang"], prefixes=[".", "/", "!"]))
async def kang_cmd(client: Client, message: Message):
    reply = message.reply_to_message
    if not reply:
        return await message.reply_text("<blockquote>⚠️ <b>Kisi photo ya sticker par reply karke .kang use karein!</b></blockquote>")

    status = await message.reply_text("<blockquote>⏳ <b>Kanging sticker...</b></blockquote>")

    emoji = "🤔"
    if len(message.command) > 1:
        emoji = message.command[1]
    elif reply.sticker and reply.sticker.emoji:
        emoji = reply.sticker.emoji

    user = message.from_user
    if not user:
        return await status.edit("<blockquote>❌ <b>Anonymous users pack create nahi kar sakte!</b></blockquote>")

    bot_user = await client.get_me()
    bot_username = bot_user.username
    bot_token = os.environ.get("BOT_TOKEN")

    temp_path = None
    try:
        temp_path = await reply.download()
        if not temp_path:
            return await status.edit("<blockquote>❌ <b>Media download fail hua!</b></blockquote>")

        im = Image.open(temp_path)
        im.thumbnail((512, 512))
        
        bio = io.BytesIO()
        bio.name = "sticker.webp"
        im.save(bio, format="WEBP")
        bio.seek(0)
        sticker_bytes = bio.getvalue()

        pack_num = 1
        pack_name = f"a{user.id}_by_{bot_username}"
        pack_title = f"{user.first_name[:20]}'s Kang Pack"

        check_pack = await client.loop.run_in_executor(
            None, 
            call_bot_api, 
            bot_token, 
            "getStickerSet", 
            {"name": pack_name}
        )

        pack_exists = check_pack.get("ok", False)
        stickers_count = len(check_pack.get("result", {}).get("stickers", [])) if pack_exists else 0

        if pack_exists and stickers_count >= 120:
            pack_num += 1
            pack_name = f"a{pack_num}_{user.id}_by_{bot_username}"
            pack_title = f"{user.first_name[:20]}'s Kang Pack Vol {pack_num}"
            check_pack = await client.loop.run_in_executor(
                None, 
                call_bot_api, 
                bot_token, 
                "getStickerSet", 
                {"name": pack_name}
            )
            pack_exists = check_pack.get("ok", False)
            stickers_count = len(check_pack.get("result", {}).get("stickers", [])) if pack_exists else 0

        sticker_obj = {
            "sticker": "attach://sticker_file",
            "emoji_list": [emoji],
            "format": "static"
        }

        if not pack_exists:
            res = await client.loop.run_in_executor(
                None,
                call_bot_api,
                bot_token,
                "createNewStickerSet",
                {
                    "user_id": user.id,
                    "name": pack_name,
                    "title": pack_title,
                    "stickers": json.dumps([sticker_obj])
                },
                {"sticker_file": ("sticker.webp", sticker_bytes, "image/webp")}
            )
            stickers_count = 1
        else:
            res = await client.loop.run_in_executor(
                None,
                call_bot_api,
                bot_token,
                "addStickerToSet",
                {
                    "user_id": user.id,
                    "name": pack_name,
                    "sticker": json.dumps(sticker_obj)
                },
                {"sticker_file": ("sticker.webp", sticker_bytes, "image/webp")}
            )
            stickers_count += 1

        if not res.get("ok"):
            err = res.get("description", "Unknown error")
            if "PEER_ID_INVALID" in err or "user not found" in err.lower():
                return await status.edit("<blockquote>❌ <b>Pehle mujhe DM (PM) me /start karo taaki main aapka pack bana saku!</b></blockquote>")
            return await status.edit(f"<blockquote>❌ <b>API Error:</b> {err}</blockquote>")

        pack_link = f"https://t.me/addstickers/{pack_name}"

        # MongoDB me pack details save/update
        if kang_db is not None:
            try:
                await kang_db.update_one(
                    {"user_id": user.id, "pack_name": pack_name},
                    {
                        "$set": {
                            "user_id": user.id,
                            "user_name": user.first_name,
                            "pack_name": pack_name,
                            "pack_title": pack_title,
                            "pack_link": pack_link,
                            "total_stickers": stickers_count
                        }
                    },
                    upsert=True
                )
            except Exception:
                pass

        await status.edit(
            f"<blockquote>✅ <b>Sticker Kanged!</b></blockquote>\n\n"
            f"<b>Pack:</b> <a href='{pack_link}'>View Pack</a>\n"
            f"<b>Emoji:</b> {emoji}\n"
            f"<b>Total Stickers:</b> {stickers_count}",
            disable_web_page_preview=True
        )

    except Exception as e:
        await status.edit(f"<blockquote>❌ <b>Error:</b> {e}</blockquote>")
    finally:
        if temp_path and os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except Exception:
                pass
                
