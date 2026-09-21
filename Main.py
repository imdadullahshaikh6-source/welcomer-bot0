import os
from pyrogram import Client

API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
STRING_SESSION = os.environ.get("STRING_SESSION")

# plugins folder specify kar diya jahan se bot sari files uthayega
plugins = dict(root="plugins")

app = Client(
    "userbot",
    api_id=API_ID,
    api_hash=API_HASH,
    session_string=STRING_SESSION,
    plugins=plugins
)

if __name__ == "__main__":
    print("Userbot with Modular Plugins Live ho gaya!")
    app.run()
    
