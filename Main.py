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

@app.on_message(filters.command(["start", "stop"], prefixes=[".", "/"]) & filters.user(OWNER_ID))
async def control_bot(client, message):
    global IS_ACTIVE
    command = message.text.lower()
    
    if "start" in command:
        if IS_ACTIVE:
            await message.reply_text("Welcomer Bot pehle se hi **ON** hai! ✅")
        else:
            IS_ACTIVE = True
            await message.reply_text("Welcomer Bot ko **START** kar diya gaya hai! 🟢")
            
    elif "stop" in command:
        if not IS_ACTIVE:
            await message.reply_text("Welcomer Bot pehle se hi **STOP** hai! 🛑")
        else:
            IS_ACTIVE = False
            await message.reply_text("Welcomer Bot ko **STOP** kar diya gaya hai! 🔴")

@app.on_chat_join_request()
async def auto_accept_and_welcome(client, request):
    global IS_ACTIVE
    if not IS_ACTIVE:
        return
        
    chat_id = request.chat.id
    user = request.from_user
    
    try:
        # 1. Join request accept karna
        await client.approve_chat_join_request(chat_id, user.id)
        
        # 2. 5 second wait ke sath typing show karna
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
        print(f"Error handling request: {e}")

if __name__ == "__main__":
    print("Userbot Request Welcomer Live ho gaya!")
    app.run ()
  
  
