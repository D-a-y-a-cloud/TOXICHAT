"""
Database layer — MongoDB with in-memory fallback.
Uses motor (async MongoDB driver) when MongoDB is available,
falls back to an in-memory dict store otherwise.
"""
import os
import asyncio
from datetime import datetime
from typing import Optional, List

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))
    print("[OK] Loaded .env file")
except ImportError:
    print("[WARN] python-dotenv not installed, using system environment variables")

# Try MongoDB, fall back to in-memory
MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "toxichat")

_db = None
_use_memory = False
_memory_store = {"users": [], "messages": [], "groups": []}


async def get_db():
    """Return the database connection (MongoDB or in-memory fallback)."""
    global _db, _use_memory
    if _db is not None and _db != "memory":
        return _db
    
    print(f"📡 Attempting to connect to MongoDB: {DB_NAME}...")
    try:
        from motor.motor_asyncio import AsyncIOMotorClient
        import certifi
        # Fix SSL Handshake errors by using certifi and specific timeout
        client = AsyncIOMotorClient(
            MONGO_URL, 
            serverSelectionTimeoutMS=5000, 
            tlsCAFile=certifi.where()
        )
        await client.admin.command("ping")
        _db = client[DB_NAME]
        _use_memory = False
        print(f"✅ [SUCCESS] Connected to MongoDB Atlas: {DB_NAME}")
        
        # Create indexes
        await _db.users.create_index("username", unique=True)
        await _db.messages.create_index("timestamp")
        return _db
    except Exception as e:
        print(f"⚠️ [FALLBACK] MongoDB connection failed: {e}")
        print("💾 Defaulting to In-Memory storage mode for this session.")
        _use_memory = True
        _db = "memory"
        return _db


def is_memory_mode():
    return _use_memory


# ══════════════════════════════════════════════════════════════
# CRUD Operations (work for both MongoDB and in-memory)
# ══════════════════════════════════════════════════════════════

# ── Users ────────────────────────────────────────────────────
async def create_user(username: str, hashed_password: str, display_name: str) -> dict:
    user = {
        "username": username,
        "password": hashed_password,
        "display_name": display_name,
        "created_at": datetime.utcnow().isoformat(),
        "is_online": False,
        "warnings_count": 0,
        "is_blocked": False,
    }
    if _use_memory:
        if any(u["username"] == username for u in _memory_store["users"]):
            raise ValueError("Username already exists")
        _memory_store["users"].append(user)
    else:
        db = await get_db()
        await db.users.insert_one(user.copy())
    return user


async def get_user(username: str) -> Optional[dict]:
    if _use_memory:
        return next((u for u in _memory_store["users"] if u["username"] == username), None)
    db = await get_db()
    return await db.users.find_one({"username": username}, {"_id": 0})


async def set_user_online(username: str, online: bool):
    if _use_memory:
        for u in _memory_store["users"]:
            if u["username"] == username:
                u["is_online"] = online
    else:
        db = await get_db()
        await db.users.update_one({"username": username}, {"$set": {"is_online": online}})


async def increment_warning_count(username: str) -> int:
    user = await get_user(username)
    if not user:
        return 0
    new_count = user.get("warnings_count", 0) + 1
    new_blocked = new_count >= 20

    if _use_memory:
        for u in _memory_store["users"]:
            if u["username"] == username:
                u["warnings_count"] = new_count
                u["is_blocked"] = new_blocked
    else:
        db = await get_db()
        await db.users.update_one(
            {"username": username}, 
            {"$set": {"warnings_count": new_count, "is_blocked": new_blocked}}
        )
    return new_count


async def get_all_users() -> List[dict]:
    if _use_memory:
        return [{"username": u["username"], "display_name": u["display_name"],
                 "is_online": u.get("is_online", False)} for u in _memory_store["users"]]
    db = await get_db()
    cursor = db.users.find({}, {"_id": 0, "password": 0})
    return await cursor.to_list(length=500)


# ── Messages ─────────────────────────────────────────────────
async def save_message(msg: dict) -> dict:
    msg["timestamp"] = datetime.utcnow().isoformat()
    msg["id"] = f"msg_{datetime.utcnow().timestamp()}"
    if _use_memory:
        _memory_store["messages"].append(msg)
    else:
        db = await get_db()
        await db.messages.insert_one(msg.copy())
    return msg


async def get_messages(user1: str, user2: str, limit: int = 50) -> List[dict]:
    if _use_memory:
        msgs = [m for m in _memory_store["messages"]
                if not m.get("is_group") and
                ((m["sender"] == user1 and m["receiver"] == user2) or
                 (m["sender"] == user2 and m["receiver"] == user1))]
        return msgs[-limit:]
    db = await get_db()
    cursor = db.messages.find(
        {"$or": [
            {"sender": user1, "receiver": user2, "is_group": False},
            {"sender": user2, "receiver": user1, "is_group": False}
        ]},
        {"_id": 0}
    ).sort("timestamp", -1).limit(limit)
    msgs = await cursor.to_list(length=limit)
    return list(reversed(msgs))


async def get_group_messages(group: str, limit: int = 50) -> List[dict]:
    if _use_memory:
        msgs = [m for m in _memory_store["messages"]
                if m.get("is_group") and m["receiver"] == group]
        return msgs[-limit:]
    db = await get_db()
    cursor = db.messages.find(
        {"receiver": group, "is_group": True}, {"_id": 0}
    ).sort("timestamp", -1).limit(limit)
    msgs = await cursor.to_list(length=limit)
    return list(reversed(msgs))


# ── Dashboard Stats ──────────────────────────────────────────
async def get_dashboard_stats() -> dict:
    if _use_memory:
        msgs = _memory_store["messages"]
    else:
        db = await get_db()
        msgs = await db.messages.find({}, {"_id": 0}).to_list(length=10000)

    total = len(msgs)
    toxic = sum(1 for m in msgs if m.get("is_flagged", False))
    non_toxic = total - toxic

    # Most toxic users
    user_toxic = {}
    for m in msgs:
        if m.get("is_flagged"):
            user_toxic[m["sender"]] = user_toxic.get(m["sender"], 0) + 1
    top_users = sorted(user_toxic.items(), key=lambda x: x[1], reverse=True)[:10]
    top_users = [{"username": u, "toxic_count": c} for u, c in top_users]

    # Hourly trend (group by hour from timestamp)
    hourly = {}
    for m in msgs:
        try:
            h = datetime.fromisoformat(m["timestamp"]).hour
        except:
            h = 0
        if h not in hourly:
            hourly[h] = {"hour": h, "total": 0, "toxic": 0}
        hourly[h]["total"] += 1
        if m.get("is_flagged"):
            hourly[h]["toxic"] += 1
    trend = sorted(hourly.values(), key=lambda x: x["hour"])

    return {
        "total_messages": total,
        "toxic_count": toxic,
        "non_toxic_count": non_toxic,
        "toxicity_rate": round(toxic / max(total, 1), 4),
        "most_toxic_users": top_users,
        "hourly_trend": trend,
    }


# ── Groups ───────────────────────────────────────────────────
async def create_group(name: str, members: List[str], creator: str) -> dict:
    group = {"name": name, "members": list(set(members + [creator])), "creator": creator,
             "created_at": datetime.utcnow().isoformat()}
    if _use_memory:
        _memory_store["groups"].append(group)
    else:
        db = await get_db()
        await db.groups.insert_one(group.copy())
    return group


async def get_user_groups(username: str) -> List[dict]:
    if _use_memory:
        return [g for g in _memory_store["groups"] if username in g.get("members", [])]
    db = await get_db()
    cursor = db.groups.find({"members": username}, {"_id": 0})
    return await cursor.to_list(length=100)
