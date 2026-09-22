import os
from motor.motor_asyncio import AsyncIOMotorClient

MONGO_URL = os.getenv("MONGO_URL")

if MONGO_URL:
    client = AsyncIOMotorClient(MONGO_URL)
    db = client["WelcomerBotDB"]
    welcome_col = db["welcome_settings"]
    req_col = db["request_accept"]
    warn_col = db["warns"]
    mute_col = db["muted_users"]
    ban_col = db["banned_users"]
else:
    client = None
    db = None
    welcome_col = None
    req_col = None
    warn_col = None
    mute_col = None
    ban_col = None

# ==================== WELCOME SETTINGS ====================
async def get_welcome_db(chat_id: int):
    if welcome_col is not None:
        return await welcome_col.find_one({"chat_id": chat_id})
    return None

async def set_welcome_db(chat_id: int, data: dict):
    if welcome_col is not None:
        await welcome_col.update_one(
            {"chat_id": chat_id},
            {"$set": data},
            upsert=True
        )

async def toggle_welcome_db(chat_id: int, status: bool):
    if welcome_col is not None:
        await welcome_col.update_one(
            {"chat_id": chat_id},
            {"$set": {"enabled": status}},
            upsert=True
        )

async def reset_welcome_db(chat_id: int):
    if welcome_col is not None:
        await welcome_col.delete_one({"chat_id": chat_id})

# ==================== REQUEST ACCEPT ====================
async def is_request_accept_on(chat_id: int) -> bool:
    if req_col is not None:
        doc = await req_col.find_one({"chat_id": chat_id})
        return bool(doc and doc.get("status") is True)
    return False

async def set_request_accept(chat_id: int, status: bool):
    if req_col is not None:
        await req_col.update_one(
            {"chat_id": chat_id},
            {"$set": {"status": status}},
            upsert=True
        )
        
