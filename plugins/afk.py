import time
from pyrogram import Client, filters

AFK_USERS = {}

def get_readable_time(seconds: int) -> str:
    count = 0
    ping_time = ""
    time_list = []
    time_suffix_list = ["s", "m", "h", "days"]

    while count < 4:
        count += 1
        remainder, result = divmod(seconds, 60) if count < 3 else divmod(seconds, 24)
        if seconds == 0 and remainder == 0:
            break
        time_list.append(int(result))
        seconds = int(remainder)

    for x in range(len(time_list)):
        time_list[x] = str(time_list[x]) + time_suffix_list[x]
    if len(time_list) == 4:
        ping_time += time_list.pop() + ", "

    time_list.reverse()
    ping_time += ":".join(time_list)
    return ping_time or "0s"

@Client.on_message(filters.command("afk", prefixes=[".", "/"]) & filters.group)
async def set_afk(client, message):
    user = message.from_user
    if not user:
        return
        
    reason = "Busy"
    if len(message.text.split()) > 1:
        reason = message.text.split(None, 1)[1]
        
    AFK_USERS[user.id] = {
        "reason": reason,
        "time": time.time()
    }
    mention = f"[{user.first_name}](tg://user?id={user.id})"
    await message.reply_text(f"{mention} ab **AFK** hai!\n**Wajah:** `{reason}`")

@Client.on_message(filters.group, group=1)
async def afk_listener(client, message):
    user = message.from_user
    if not user:
        return

    # User wapas aaya
    if user.id in AFK_USERS:
        afk_data = AFK_USERS.pop(user.id)
        afk_duration = get_readable_time(int(time.time() - afk_data["time"]))
        mention = f"[{user.first_name}](tg://user?id={user.id})"
        await message.reply_text(f"Welcome back {mention}! Aap **{afk_duration}** tak AFK the.")

    # Reply diya gaya AFK user ko
    if message.reply_to_message and message.reply_to_message.from_user:
        replied_user = message.reply_to_message.from_user
        if replied_user.id in AFK_USERS:
            afk_data = AFK_USERS[replied_user.id]
            afk_duration = get_readable_time(int(time.time() - afk_data["time"]))
            mention = f"[{replied_user.first_name}](tg://user?id={replied_user.id})"
            await message.reply_text(
                f"{mention} abhi **AFK** hai!\n"
                f"**Reason:** `{afk_data['reason']}`\n"
                f"**Last seen:** `{afk_duration}` pehle"
            )
            return

    # Text mention check
    if message.entities:
        for ent in message.entities:
            tagged_user_id = None
            if ent.type.name == "TEXT_MENTION" and ent.user:
                tagged_user_id = ent.user.id

            if tagged_user_id and tagged_user_id in AFK_USERS:
                afk_data = AFK_USERS[tagged_user_id]
                afk_duration = get_readable_time(int(time.time() - afk_data["time"]))
                mention = f"[{ent.user.first_name}](tg://user?id={tagged_user_id})"
                await message.reply_text(
                    f"{mention} abhi **AFK** hai!\n"
                    f"**Reason:** `{afk_data['reason']}`\n"
                    f"**Last seen:** `{afk_duration}` pehle"
                )
                break
              
