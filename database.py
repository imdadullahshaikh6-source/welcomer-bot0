# ==================== 5. AUTO ACCEPT REQUESTS ====================
req_col = db["request_accept"] if db is not None else None

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
        
