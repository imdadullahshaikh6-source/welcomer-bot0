from pyrogram import Client, filters
from pyrogram.enums import ParseMode

@Client.on_message(filters.command(["pin", "unpin"], prefixes=[".", "/"]) & filters.group)
async def simple_pin_unpin(client: Client, message):
    if not message.reply_to_message:
        return await message.reply_text("<blockquote>⚠️ Jis message ko pin/unpin karna hai uspar reply karein!</blockquote>", parse_mode=ParseMode.HTML)

    cmd = message.command[0].lower()
    try:
        if cmd == "pin":
            await client.pin_chat_message(message.chat.id, message.reply_to_message.id)
            await message.reply_text("<blockquote>📌 <b>Message Pinned!</b></blockquote>", parse_mode=ParseMode.HTML)
        else:
            await client.unpin_chat_message(message.chat.id, message.reply_to_message.id)
            await message.reply_text("<blockquote>📌 <b>Message Unpinned!</b></blockquote>", parse_mode=ParseMode.HTML)
    except Exception:
        await message.reply_text("<blockquote>⚠️ <b>Pehle mujhe admin banayein aur 'Pin Messages' permission dein!</b></blockquote>", parse_mode=ParseMode.HTML)
        
