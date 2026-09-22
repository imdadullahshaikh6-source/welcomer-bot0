import os
from motor.motor_asyncio import AsyncIOMotorClient

MONGO_URL = os.getenv("MONGO_URL")

if MONGO_URL:
    client = AsyncIOMotorClient(MONGO_URL)
    db = client["WelcomerBotDB"]
    welcome_col = db["welcome_settings"]
    warn_col = db["warns"]
    mute_col = db["muted_users"]
    ban_col = db["banned_users"]
else:
    client = None
    db = None
    welcome_col = None
    warn_col = None
    mute_col = None
    ban_col = None

# ==================== 1. WELCOME DATA ====================
async def get_welcome_data(chat_id: int):
    if welcome_col is not None:
        return await welcome_col.find_one({"chat_id": chat_id})
    return None

async def save_welcome_data(chat_id: int, text: str, file_id: str = None, media_type: str = None):
    if welcome_col is not None:
        await welcome_col.update_one(
            {"chat_id": chat_id},
            {"$set": {
                "text": text,
                "file_id": file_id,
                "media_type": media_type
            }},
            upsert=True
        )

# ==================== 2. WARNS DATA ====================
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

# ==================== 3. MUTE DATA ====================
async def save_muted_user(chat_id: int, user_id: int, reason: str = "No reason"):
    if mute_col is not None:
        await mute_col.update_one(
            {"chat_id": chat_id, "user_id": user_id},
            {"$set": {"status": "muted", "reason": reason}},
            upsert=True
        )

async def remove_muted_user(chat_id: int, user_id: int):
    if mute_col is not None:
        await mute_col.delete_one({"chat_id": chat_id, "user_id": user_id})

# ==================== 4. BAN DATA ====================
async def save_banned_user(chat_id: int, user_id: int, reason: str = "Rules violation"):
    if ban_col is not None:
        await ban_col.update_one(
            {"chat_id": chat_id, "user_id": user_id},
            {"$set": {"status": "banned", "reason": reason}},
            upsert=True
        )

async def remove_banned_user(chat_id: int, user_id: int):
    if ban_col is not None:
        await ban_col.delete_one({"chat_id": chat_id, "user_id": user_id})
        
