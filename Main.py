import asyncio
import os
from pyrogram import Client, filters, errors
from pyrogram.enums import ChatAction

API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
STRING_SESSION = os.environ.get("STRING_SESSION")
OWNER_ID = int(os.environ.get("OWNER_ID"))

app = Client("userbot", api_id=API_ID, api_hash=API_HASH, session_string=STRING_SESSION)

IS_ACTIVE = True
TASK_RUNNING = False

async def process_all_pending_requests(client, chat_id):
    global IS_ACTIVE, TASK_RUNNING
    if TASK_RUNNING:
        return
    TASK_RUNNING = True
    
    try:
        # Ek-ek karke pending join requests fetch karna
        async for req in client.get_chat_join_requests(chat_id):
            if not IS_ACTIVE:
                break
                
            user = req.user
            try:
                # 1. Approve request
                await client.approve_chat_join_request(chat_id, user.id)
                
                # 2. 5 second typing show karna
                await client.send_chat_action(chat_id, ChatAction.TYPING)
                await asyncio.sleep(5)
                
                # 3. Mention ke sath welcome message
                mention = f"[{user.first_name}](tg://user?id={user.id})"
                await client.send_message(chat_id, f"Welcome 🤗🤗 {mention}")
                
                # 4. Agle request ke liye 10 second rukna
                await asyncio.sleep(10)
                
            except errors.FloodWait as e:
                await asyncio.sleep(e.value)
            except Exception as e:
                print(f"Error processing user {user.id}: {e}")
                
    except Exception as e:
        print(f"Error fetching join requests: {e}")
    finally:
        TASK_RUNNING = False

@app.on_message(filters.command(["start", "stop"], prefixes=[".", "/"]) & filters.user(OWNER_ID))
async def control_bot(client, message):
    global IS_ACTIVE
    command = message.text.lower()
    chat_id = message.chat.id
    
    if "start" in command:
        IS_ACTIVE = True
        await message.reply_text("Welcomer Bot **START** ho gaya hai! Purani pending requests process ho rahi hain... 🟢")
        asyncio.create_task(process_all_pending_requests(client, chat_id))
            
    elif "stop" in command:
        IS_ACTIVE = False
        await message.reply_text("Welcomer Bot ko **STOP** kar diya gaya hai! 🛑")

@app.on_chat_join_request()
async def auto_accept_live(client, request):
    global IS_ACTIVE
    if not IS_ACTIVE:
        return
        
    chat_id = request.chat.id
    user = request.from_user
    
    try:
        await client.approve_chat_join_request(chat_id, user.id)
        await client.send_chat_action(chat_id, ChatAction.TYPING)
        await asyncio.sleep(5)
        mention = f"[{user.first_name}](tg://user?id={user.id})"
        await client.send_message(chat_id, f"Welcome 🤗🤗 {mention}")
        await asyncio.sleep(10)
    except errors.FloodWait as e:
        await asyncio.sleep(e.value)
    except Exception as e:
        print(f"Live request error: {e}")

if __name__ == "__main__":
    print("Userbot live...")
    app.run()
    
