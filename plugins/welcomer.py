import asyncio
import re
from pyrogram import Client, filters, errors
from pyrogram.enums import ChatAction

ITACHI_ID = 8373739674
IS_ACTIVE = True
TASK_RUNNING = False

async def is_authorized(client, message):
    if not message.from_user:
        return False
    if message.from_user.id == ITACHI_ID:
        return True
    try:
        member = await client.get_chat_member(message.chat.id, message.from_user.id)
        if member.status.name in ["OWNER", "ADMINISTRATOR"]:
            return True
    except Exception:
        pass
    return False

async def process_requests(client, chat_id):
    global IS_ACTIVE, TASK_RUNNING
    if TASK_RUNNING:
        return
    TASK_RUNNING = True
    try:
        chat = await client.get_chat(chat_id)
        async for req in client.get_chat_join_requests(chat.id):
            if not IS_ACTIVE:
                break
            try:
                await client.approve_chat_join_request(chat.id, req.user.id)
                await client.send_chat_action(chat.id, ChatAction.TYPING)
                await asyncio.sleep(3)
                name = re.sub(r'[*_`\[\]()]', '', req.user.first_name or "User")
                await client.send_message(chat.id, f"Welcome 🤗🤗 [{name}](tg://user?id={req.user.id})")
                await asyncio.sleep(6)
            except errors.FloodWait as e:
                await asyncio.sleep(e.value)
            except Exception as e:
                print(f"Join error: {e}")
    except Exception as e:
        print(f"Fetch requests error: {e}")
    finally:
        TASK_RUNNING = False

@Client.on_message(filters.command(["start", "stop"], prefixes=[".", "/"]) & filters.group)
async def start_stop_toggle(client, message):
    if not await is_authorized(client, message):
        return
    global IS_ACTIVE
    cmd = message.command[0].lower()
    if cmd == "start":
        IS_ACTIVE = True
        await message.reply_text("🟢 **Welcomer Bot START ho gaya! Requests process ho rahi hain...**")
        asyncio.create_task(process_requests(client, message.chat.id))
    elif cmd == "stop":
        IS_ACTIVE = False
        await message.reply_text("🛑 **Welcomer Bot STOP ho gaya!**")

@Client.on_chat_join_request()
async def auto_accept_live(client, request):
    global IS_ACTIVE
    if not IS_ACTIVE:
        return
    try:
        await client.approve_chat_join_request(request.chat.id, request.from_user.id)
        await client.send_chat_action(request.chat.id, ChatAction.TYPING)
        await asyncio.sleep(3)
        name = re.sub(r'[*_`\[\]()]', '', request.from_user.first_name or "User")
        await client.send_message(request.chat.id, f"Welcome 🤗🤗 [{name}](tg://user?id={request.from_user.id})")
    except Exception as e:
        print(f"Live request error: {e}")
        
