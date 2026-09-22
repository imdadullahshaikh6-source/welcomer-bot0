import os
from motor.motor_asyncio import AsyncIOMotorClient

MONGO_URL = os.getenv("MONGO_URL")

if MONGO_URL:
    client = AsyncIOMotorClient(MONGO_URL)
    db = client["WelcomerBotDB"]
    welcome_col = db["welcome_settings"]
    warn_col = db["warns"]
else:
    client = None
    db = None
    welcome_col = None
    warn_col = None

# ==================== WELCOME SETTINGS ====================
async def get_welcome(chat_id: int):
    if welcome_col is not None:
        data = await welcome_col.find_one({"chat_id": chat_id})
        return data.get("text") if data else None
    return None

async def set_welcome(chat_id: int, text: str):
    if welcome_col is not None:
        await welcome_col.update_one(
            {"chat_id": chat_id},
            {"$set": {"text": text}},
            upsert=True
        )

# ==================== WARNS STORAGE ====================
async def get_user_warns(chat_id: int, user_id: int):
    if warn_col is not None:
        data = await warn_col.find_one({"chat_id": chat_id, "user_id": user_id})
        return data.get("count", 0) if data else 0
    return 0

async def add_warn(chat_id: int, user_id: int):
    if warn_col is not None:
        data = await warn_col.find_one_and_update(
            {"chat_id": chat_id, "user_id": user_id},
            {"$inc": {"count": 1}},
            upsert=True,
            return_document=True
        )
        return data.get("count", 1)
    return 0

async def remove_warn(chat_id: int, user_id: int):
    if warn_col is not None:
        data = await warn_col.find_one({"chat_id": chat_id, "user_id": user_id})
        if data and data.get("count", 0) > 0:
            new_count = data["count"] - 1
            await warn_col.update_one(
                {"chat_id": chat_id, "user_id": user_id},
                {"$set": {"count": new_count}}
            )
            return new_count
    return 0

async def reset_user_warns(chat_id: int, user_id: int):
    if warn_col is not None:
        await warn_col.delete_one({"chat_id": chat_id, "user_id": user_id})
      
