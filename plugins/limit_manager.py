# limit_manager.py
from datetime import datetime, timedelta
from info import ENABLE_FREE_LIMIT, FREE_DAILY_LIMIT, LIMIT_RESET_HOURS
from motor.motor_asyncio import AsyncIOMotorClient
import os

# --- MongoDB Setup ---
MONGO_URI = os.environ.get("MONGO_URI") or "mongodb+srv://your_connection_string"
client = AsyncIOMotorClient(MONGO_URI)
db = client["Auto_Filter_Bot"]
user_data = db["user_limits"]


# 🕒 Get user usage (and auto reset)
async def get_user_limit(user_id: int):
    user = await user_data.find_one({"user_id": user_id})
    now = datetime.utcnow()

    if not user:
        await user_data.insert_one({
            "user_id": user_id,
            "used_count": 0,
            "last_reset": now
        })
        return 0

    last_reset = user.get("last_reset", now)
    # Reset if 24h+ passed
    if now - last_reset > timedelta(hours=LIMIT_RESET_HOURS):
        await user_data.update_one(
            {"user_id": user_id},
            {"$set": {"used_count": 0, "last_reset": now}}
        )
        return 0

    return user.get("used_count", 0)


# ➕ Increment user usage
async def increment_user_limit(user_id: int):
    await user_data.update_one(
        {"user_id": user_id},
        {
            "$inc": {"used_count": 1},
            "$setOnInsert": {"last_reset": datetime.utcnow()}
        },
        upsert=True
    )
