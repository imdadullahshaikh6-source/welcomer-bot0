import time
import re
from pyrogram import Client, filters

AFK_USERS = {}

def get_readable_time(seconds: int) -> str:
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    d, h = divmod(h, 24)
    if d > 0:
        return f"{d}d {h}h"
    if h > 0:
        return f"{h}h {m}m"
    if m > 0:
        return f"{m}m {s}s"
    return f"{s}s"

@Client.on_message(filters.command("afk", prefixes=[".", "/"]) & filters.group)
async def afk_handler(client, message):
    user = message.from_user
    if not user:
        return
    reason = "Busy"
    if len(message.command) > 1:
        reason = message.text.split(None, 1)[1]
    
    AFK_USERS[user.id] = {"reason": reason, "time": time.time()}
    name = re.sub(r'[*_`\[\]()]', '', user.first_name or "User")
    await message.reply_text(
        f"> 💤 **AFK Notice**\n"
        f"> 👤 User: [{name}](tg://user?id={user.id})\n"
        f"> 📝 Reason: `{reason}`"
    )

@Client.on_message(filters.group, group=1)
async def afk_watcher(client, message):
    user = message.from_user
    if not user:
        return

    # 1. User wapas aaya
    if user.id in AFK_USERS and not (message.text and message.text.startswith((".", "/"))):
        data = AFK_USERS.pop(user.id)
        dur = get_readable_time(int(time.time() - data["time"]))
        name = re.sub(r'[*_`\[\]()]', '', user.first_name or "User")
        await message.reply_text(
            f"> 👋 **Welcome Back!**\n"
            f"> 👤 [{name}](tg://user?id={user.id}) ab online hain.\n"
            f"> ⏳ Duration: `{dur}`"
        )

    # 2. AFK user ko reply kiya
    if message.reply_to_message and message.reply_to_message.from_user:
        rep = message.reply_to_message.from_user
        if rep.id in AFK_USERS:
            data = AFK_USERS[rep.id]
            dur = get_readable_time(int(time.time() - data["time"]))
            name = re.sub(r'[*_`\[\]()]', '', rep.first_name or "User")
            await message.reply_text(
                f"> ⚠️ **User is Currently AFK!**\n"
                f"> 👤 User: [{name}](tg://user?id={rep.id})\n"
                f"> 📝 Reason: `{data['reason']}`\n"
                f"> ⏳ Duration: `{dur}`"
            )
            return

    # 3. AFK user ko tag kiya
    if message.entities:
        for ent in message.entities:
            if ent.type.name == "TEXT_MENTION" and ent.user and ent.user.id in AFK_USERS:
                data = AFK_USERS[ent.user.id]
                dur = get_readable_time(int(time.time() - data["time"]))
                name = re.sub(r'[*_`\[\]()]', '', ent.user.first_name or "User")
                await message.reply_text(
                    f"> ⚠️ **User is Currently AFK!**\n"
                    f"> 👤 User: [{name}](tg://user?id={ent.user.id})\n"
                    f"> 📝 Reason: `{data['reason']}`\n"
                    f"> ⏳ Duration: `{dur}`"
                )
                break
                
