import io
import html
import aiohttp
from pyrogram import Client, filters
from pyrogram.enums import ParseMode

QUOTLY_API = "https://bot.lyo.su/quote/generate"

@Client.on_message(filters.command(["q", "quote"], prefixes=[".", "/"]) & filters.group)
async def quotly_command(client: Client, message):
    if not message.reply_to_message:
        return await message.reply_text(
            "<blockquote>⚠️ <b>Kisi user ke message par reply karke <code>.q</code> likhein!</b></blockquote>",
            parse_mode=ParseMode.HTML
        )

    reply_msg = message.reply_to_message
    text = reply_msg.text or reply_msg.caption or ""
    
    if not text and not reply_msg.sticker and not reply_msg.photo:
        return await message.reply_text(
            "<blockquote>⚠️ Quotly generate karne ke liye message me text hona zaroori hai!</blockquote>",
            parse_mode=ParseMode.HTML
        )

    status_msg = await message.reply_text("<blockquote>🎨 <i>Generating quote sticker...</i></blockquote>", parse_mode=ParseMode.HTML)

    # User profile photo fetch
    avatar_url = None
    sender = reply_msg.from_user or reply_msg.sender_chat
    sender_id = sender.id if sender else 0
    sender_name = getattr(sender, "first_name", getattr(sender, "title", "User"))

    # Payload setup for Quotly API
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
                    "id": sender_id,
                    "name": sender_name,
                    "photo": {}
                },
                "text": text or "📷 [Photo / Media]",
                "replyMessage": {}
            }
        ]
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(QUOTLY_API, json=payload, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    image_bytes = data.get("result", {}).get("image")
                    if image_bytes:
                        import base64
                        raw_webp = base64.b64decode(image_bytes)
                        bio = io.BytesIO(raw_webp)
                        bio.name = "quote.webp"
                        await client.send_sticker(
                            chat_id=message.chat.id,
                            sticker=bio,
                            reply_to_message_id=reply_msg.id
                        )
                        return await status_msg.delete()
                
                await status_msg.edit_text(
                    f"<blockquote>⚠️ <b>Quotly API Error:</b> Status code {resp.status}</blockquote>",
                    parse_mode=ParseMode.HTML
                )
    except Exception as e:
        await status_msg.edit_text(
            f"<blockquote>⚠️ <b>Quotly Failed:</b> <code>{html.escape(str(e))}</code></blockquote>",
            parse_mode=ParseMode.HTML
        )
        
