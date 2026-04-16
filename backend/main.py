"""
ToxiChat — FastAPI Backend
Real-time chat with ML-powered toxicity detection.
"""
import os
import json
import asyncio
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Dict, Set

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from jose import jwt, JWTError
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from models import (UserRegister, UserLogin, TokenOut, UserOut,
                    MessageIn, MessageOut, ToxicityRequest, ToxicityResult,
                    DashboardStats, GroupCreate)
import database as db
import ml_service

# ══════════════════════════════════════════════════════════════
# CONFIG
# ══════════════════════════════════════════════════════════════
SECRET_KEY = os.getenv("SECRET_KEY", "toxichat-secret-key-change-in-prod")
ALGORITHM = "HS256"
TOKEN_EXPIRE_HOURS = 24


# Simple password hashing (no bcrypt dependency issues)
def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    hashed = hashlib.sha256((salt + password).encode()).hexdigest()
    return f"{salt}${hashed}"


def verify_password(password: str, stored: str) -> bool:
    salt, hashed = stored.split("$", 1)
    return hashlib.sha256((salt + password).encode()).hexdigest() == hashed

app = FastAPI(title="ToxiChat API", version="1.0.0",
              description="WhatsApp-like chat with real-time toxicity detection")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ══════════════════════════════════════════════════════════════
# AUTH HELPERS
# ══════════════════════════════════════════════════════════════
def create_token(username: str) -> str:
    expire = datetime.utcnow() + timedelta(hours=TOKEN_EXPIRE_HOURS)
    return jwt.encode({"sub": username, "exp": expire}, SECRET_KEY, algorithm=ALGORITHM)


def verify_token(token: str) -> str:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if not username:
            raise HTTPException(401, "Invalid token")
        return username
    except JWTError:
        raise HTTPException(401, "Invalid or expired token")


# ══════════════════════════════════════════════════════════════
# STARTUP
# ══════════════════════════════════════════════════════════════
@app.on_event("startup")
async def startup():
    await db.get_db()
    print("[OK] ToxiChat API is ready!")


# ══════════════════════════════════════════════════════════════
# AUTH ROUTES
# ══════════════════════════════════════════════════════════════
@app.post("/api/register", response_model=TokenOut)
async def register(data: UserRegister):
    existing = await db.get_user(data.username)
    if existing:
        raise HTTPException(400, "Username already taken")
    hashed = hash_password(data.password)
    display = data.display_name or data.username
    await db.create_user(data.username, hashed, display)
    token = create_token(data.username)
    return TokenOut(access_token=token, username=data.username, display_name=display)


@app.post("/api/login", response_model=TokenOut)
async def login(data: UserLogin):
    user = await db.get_user(data.username)
    if not user or not verify_password(data.password, user["password"]):
        raise HTTPException(401, "Invalid username or password")
    token = create_token(data.username)
    return TokenOut(access_token=token, username=data.username,
                    display_name=user.get("display_name", data.username))


@app.get("/api/users")
async def list_users():
    return await db.get_all_users()


# ══════════════════════════════════════════════════════════════
# TOXICITY PREDICTION ROUTE
# ══════════════════════════════════════════════════════════════
@app.post("/api/predict", response_model=ToxicityResult)
async def predict(data: ToxicityRequest):
    result = ml_service.predict_toxicity(data.text)
    return ToxicityResult(text=data.text, **result)


# ══════════════════════════════════════════════════════════════
# MESSAGES ROUTES
# ══════════════════════════════════════════════════════════════
@app.get("/api/messages/{user1}/{user2}")
async def get_messages(user1: str, user2: str):
    return await db.get_messages(user1, user2)


@app.get("/api/messages/group/{group_name}")
async def get_group_msgs(group_name: str):
    return await db.get_group_messages(group_name)


# ══════════════════════════════════════════════════════════════
# GROUPS
# ══════════════════════════════════════════════════════════════
@app.post("/api/groups")
async def create_group(data: GroupCreate, token: str = ""):
    username = verify_token(token) if token else "system"
    group = await db.create_group(data.name, data.members, username)
    return {"status": "created", "group": group}


@app.get("/api/groups/{username}")
async def get_groups(username: str):
    return await db.get_user_groups(username)


# ══════════════════════════════════════════════════════════════
# DASHBOARD
# ══════════════════════════════════════════════════════════════
@app.get("/api/dashboard/stats", response_model=DashboardStats)
async def dashboard_stats():
    return await db.get_dashboard_stats()


# ══════════════════════════════════════════════════════════════
# WEBSOCKET — Real-Time Chat
# ══════════════════════════════════════════════════════════════
class ConnectionManager:
    """Manages active WebSocket connections."""

    def __init__(self):
        self.connections: Dict[str, WebSocket] = {}

    async def connect(self, username: str, websocket: WebSocket):
        await websocket.accept()
        self.connections[username] = websocket
        await db.set_user_online(username, True)
        
        await self.broadcast_user_presence(username, True)
        await self.broadcast_system(f"{username} is online", exclude=username)

    async def disconnect(self, username: str):
        self.connections.pop(username, None)
        await db.set_user_online(username, False)
        
        await self.broadcast_user_presence(username, False)
        await self.broadcast_system(f"{username} is offline")

    async def broadcast_user_presence(self, username: str, is_online: bool):
        data = {"type": "user_presence", "username": username, "is_online": is_online}
        for u, ws in list(self.connections.items()):
            if u != username:
                try:
                    await ws.send_json(data)
                except:
                    pass

    async def send_to_user(self, username: str, data: dict):
        ws = self.connections.get(username)
        if ws:
            try:
                await ws.send_json(data)
            except:
                self.connections.pop(username, None)

    async def broadcast_to_group(self, group_members: list, data: dict, exclude: str = ""):
        for member in group_members:
            if member != exclude:
                await self.send_to_user(member, data)

    async def broadcast_system(self, message: str, exclude: str = ""):
        data = {"type": "system", "message": message,
                "timestamp": datetime.utcnow().isoformat()}
        for username, ws in list(self.connections.items()):
            if username != exclude:
                try:
                    await ws.send_json(data)
                except:
                    self.connections.pop(username, None)


manager = ConnectionManager()


@app.websocket("/ws/{token}")
async def websocket_endpoint(websocket: WebSocket, token: str):
    """
    WebSocket endpoint for real-time chat.
    Message format (client → server):
    {
        "type": "message",
        "text": "Hello!",
        "receiver": "username_or_group",
        "is_group": false
    }
    """
    try:
        username = verify_token(token)
        user_data = await db.get_user(username)
        if user_data and user_data.get("is_blocked"):
            await websocket.accept()
            await websocket.send_json({"type": "system", "message": "⛔ ACCOUNT BANNED: Your account is permanently blocked due to toxicity."})
            await websocket.close(code=4003)
            return
    except:
        await websocket.close(code=4001)
        return

    await manager.connect(username, websocket)

    # Send online users list
    users = await db.get_all_users()
    await websocket.send_json({"type": "users_list", "users": users})

    try:
        while True:
            raw = await websocket.receive_text()
            data = json.loads(raw)
            msg_type = data.get("type", "message")

            if msg_type == "message":
                text = data.get("text", "").strip()
                receiver = data.get("receiver", "")
                is_group = data.get("is_group", False)

                if not text or not receiver:
                    continue

                # Check if temporarily blocked
                user_data = await db.get_user(username)
                if user_data and user_data.get("warnings_count", 0) >= 3:
                    await manager.send_to_user(username, {
                        "type": "system", 
                        "message": "❌ You are blocked from sending messages due to reaching 3 toxicity warnings."
                    })
                    continue

                # ── Predict toxicity ─────────────────────────
                tox = ml_service.predict_toxicity(text)

                # ── Save message ─────────────────────────────
                msg = await db.save_message({
                    "sender": username,
                    "receiver": receiver,
                    "text": text,
                    "is_group": is_group,
                    "toxicity_score": tox["score"],
                    "toxicity_label": tox["label"],
                    "is_flagged": tox["is_flagged"],
                })

                # ── Build response payload ───────────────────
                payload = {
                    "type": "message",
                    "id": msg["id"],
                    "sender": username,
                    "receiver": receiver,
                    "text": text,
                    "timestamp": msg["timestamp"],
                    "is_group": is_group,
                    "toxicity_score": tox["score"],
                    "toxicity_label": tox["label"],
                    "is_flagged": tox["is_flagged"],
                    "status": "sent"
                }

                # ── Send to sender (with toxicity info) ──────
                await manager.send_to_user(username, payload)

                # ── Send to receiver(s) ──────────────────────
                if is_group:
                    groups = await db.get_user_groups(username)
                    group = next((g for g in groups if g["name"] == receiver), None)
                    if group:
                        await manager.broadcast_to_group(
                            group["members"], payload, exclude=username)
                else:
                    # Add toxicity warning for receiver if flagged
                    if tox["is_flagged"]:
                        warning = {
                            "type": "toxicity_warning",
                            "message": "WARNING: The following message may contain harmful content",
                            "from": username,
                            "score": tox["score"],
                        }
                        await manager.send_to_user(receiver, warning)
                    await manager.send_to_user(receiver, payload)

                # ── Warning popup to sender if toxic ─────────
                if tox["is_flagged"]:
                    new_warnings = await db.increment_warning_count(username)
                    alert_msg = f"ALERT: Your message was flagged as potentially toxic! (Warning {new_warnings})"
                    
                    if new_warnings >= 3:
                        alert_msg = f"🛑 ACCOUNT RESTRICTED: You have reached {new_warnings} warnings and can no longer send messages."
                    if new_warnings >= 20:
                        alert_msg = "⛔ ACCOUNT BANNED: You have reached 20 warnings. Your account is permanently blocked."

                    await manager.send_to_user(username, {
                        "type": "toxicity_alert",
                        "message": alert_msg,
                        "score": tox["score"],
                        "label": tox["label"],
                    })

                    if new_warnings >= 20:
                        await manager.disconnect(username)
                        await websocket.close(code=4003)
                        return

            elif msg_type == "typing":
                receiver = data.get("receiver", "")
                await manager.send_to_user(receiver, {
                    "type": "typing", "sender": username
                })

            elif msg_type == "message_delivered" or msg_type == "message_read":
                msg_id = data.get("message_id")
                sender = data.get("sender")
                status = "read" if msg_type == "message_read" else "delivered"
                
                if msg_id:
                    await db.update_message_status(msg_id, status)
                
                if sender:
                    await manager.send_to_user(sender, {
                        "type": "message_status_update",
                        "message_id": msg_id,
                        "status": status,
                        "receiver": username
                    })

            elif msg_type == "get_users":
                users = await db.get_all_users()
                await websocket.send_json({"type": "users_list", "users": users})

    except WebSocketDisconnect:
        await manager.disconnect(username)
    except Exception as e:
        print(f"WebSocket error for {username}: {e}")
        await manager.disconnect(username)


# ══════════════════════════════════════════════════════════════
# HEALTH CHECK
# ══════════════════════════════════════════════════════════════
@app.get("/")
async def health():
    return {
        "app": "ToxiChat",
        "status": "running",
        "ml_model_loaded": ml_service._ready,
        "storage": "MongoDB" if not db.is_memory_mode() else "In-Memory",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
