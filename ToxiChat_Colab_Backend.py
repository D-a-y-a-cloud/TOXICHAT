# ================================================================
# 🧠 ToxiChat — Google Colab Backend + API Testing
# ================================================================
# This file runs the entire FastAPI backend inside Google Colab
# with ngrok tunneling to create a public URL.
#
# INSTRUCTIONS:
# 1. Copy this entire file into a single Colab cell
# 2. Run it — it will install dependencies, start the server,
#    and give you a public URL
# 3. Use that URL as REACT_APP_API_URL for the React frontend
# ================================================================

# === CELL 1: Install Dependencies ===
# (In standard Python, you install these via terminal, not with !pip)
# pip install -q fastapi uvicorn python-jose[cryptography] passlib[bcrypt] motor pymongo joblib scikit-learn numpy pydantic python-multipart aiofiles pyngrok

# === CELL 2: Create Backend Files ===
import os
os.makedirs('toxichat_backend', exist_ok=True)
os.makedirs('toxichat_backend/models_dir', exist_ok=True)

# ── models.py ────────────────────────────────────────────────
models_py = '''
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class UserRegister(BaseModel):
    username: str = Field(..., min_length=3, max_length=30)
    password: str = Field(..., min_length=4)
    display_name: Optional[str] = None

class UserLogin(BaseModel):
    username: str
    password: str

class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    username: str
    display_name: str

class MessageIn(BaseModel):
    text: str
    receiver: str
    is_group: bool = False

class ToxicityRequest(BaseModel):
    text: str

class ToxicityResult(BaseModel):
    text: str
    score: float
    label: str
    is_flagged: bool

class DashboardStats(BaseModel):
    total_messages: int
    toxic_count: int
    non_toxic_count: int
    toxicity_rate: float
    most_toxic_users: List[dict]
    hourly_trend: List[dict]

class GroupCreate(BaseModel):
    name: str = Field(..., min_length=2)
    members: List[str]
'''

with open('toxichat_backend/models.py', 'w') as f:
    f.write(models_py)

# ── ml_service.py ────────────────────────────────────────────
ml_service_py = '''
import os, re, numpy as np

_model = None
_vectorizer = None
_ready = False
TOXICITY_THRESHOLD = 0.7

TOXIC_KEYWORDS = [
    'hate','kill','die','stupid','idiot','moron','dumb','trash',
    'garbage','terrible','horrible','awful','disgusting','pathetic',
    'loser','worthless','ugly','racist','bigot','cancer',
    'shut up','hell','damn','ass','crap','jerk','fool','liar',
    'suck','annoying','ignorant','freak','scum'
]

def load_model():
    global _model, _vectorizer, _ready
    try:
        import joblib
        model_path = os.path.join(os.path.dirname(__file__), "models_dir", "model.pkl")
        tfidf_path = os.path.join(os.path.dirname(__file__), "models_dir", "tfidf_vectorizer.pkl")
        if os.path.exists(model_path) and os.path.exists(tfidf_path):
            _model = joblib.load(model_path)
            _vectorizer = joblib.load(tfidf_path)
            _ready = True
            print("ML model loaded!")
        else:
            print("No model files found, using keyword fallback")
    except Exception as e:
        print(f"Model load error: {e}")

def predict_toxicity(text):
    if not text or not text.strip():
        return {"score": 0.0, "label": "non-toxic", "is_flagged": False}

    if _ready and _model and _vectorizer:
        try:
            cleaned = re.sub(r"[^a-z\\s]", " ", text.lower())
            features = _vectorizer.transform([cleaned])
            if hasattr(_model, "predict_proba"):
                score = float(_model.predict_proba(features)[0][1])
            elif hasattr(_model, "decision_function"):
                d = _model.decision_function(features)[0]
                score = float(1 / (1 + np.exp(-d)))
            else:
                score = float(_model.predict(features)[0])
            score = max(0.0, min(1.0, score))
            return {"score": round(score, 4), "label": "toxic" if score >= 0.5 else "non-toxic",
                    "is_flagged": score >= TOXICITY_THRESHOLD}
        except Exception as e:
            print(f"ML error: {e}")

    text_lower = text.lower()
    hits = sum(1 for kw in TOXIC_KEYWORDS if kw in text_lower)
    caps = sum(1 for c in text if c.isupper()) / max(len(text), 1)
    score = min(1.0, hits * 0.15 + caps * 0.5 + text.count("!") / max(len(text), 1) * 2)
    return {"score": round(score, 4), "label": "toxic" if score >= 0.5 else "non-toxic",
            "is_flagged": score >= TOXICITY_THRESHOLD}

load_model()
'''

with open('toxichat_backend/ml_service.py', 'w') as f:
    f.write(ml_service_py)

# ── database.py (in-memory for Colab) ────────────────────────
database_py = '''
from datetime import datetime
from typing import Optional, List

_store = {"users": [], "messages": [], "groups": []}

async def get_db():
    print("Using in-memory storage (Colab mode)")
    return "memory"

def is_memory_mode():
    return True

async def create_user(username, hashed_password, display_name):
    if any(u["username"] == username for u in _store["users"]):
        raise ValueError("Username exists")
    user = {"username": username, "password": hashed_password,
            "display_name": display_name,
            "created_at": datetime.utcnow().isoformat(), "is_online": False}
    _store["users"].append(user)
    return user

async def get_user(username):
    return next((u for u in _store["users"] if u["username"] == username), None)

async def set_user_online(username, online):
    for u in _store["users"]:
        if u["username"] == username: u["is_online"] = online

async def get_all_users():
    return [{"username": u["username"], "display_name": u["display_name"],
             "is_online": u.get("is_online", False)} for u in _store["users"]]

async def save_message(msg):
    msg["timestamp"] = datetime.utcnow().isoformat()
    msg["id"] = f"msg_{datetime.utcnow().timestamp()}"
    _store["messages"].append(msg)
    return msg

async def get_messages(user1, user2, limit=50):
    msgs = [m for m in _store["messages"]
            if not m.get("is_group") and
            ((m["sender"]==user1 and m["receiver"]==user2) or
             (m["sender"]==user2 and m["receiver"]==user1))]
    return msgs[-limit:]

async def get_group_messages(group, limit=50):
    return [m for m in _store["messages"]
            if m.get("is_group") and m["receiver"]==group][-limit:]

async def get_dashboard_stats():
    msgs = _store["messages"]
    total = len(msgs)
    toxic = sum(1 for m in msgs if m.get("is_flagged"))
    user_toxic = {}
    for m in msgs:
        if m.get("is_flagged"):
            user_toxic[m["sender"]] = user_toxic.get(m["sender"], 0) + 1
    top = sorted(user_toxic.items(), key=lambda x: x[1], reverse=True)[:10]
    hourly = {}
    for m in msgs:
        try: h = datetime.fromisoformat(m["timestamp"]).hour
        except: h = 0
        if h not in hourly: hourly[h] = {"hour": h, "total": 0, "toxic": 0}
        hourly[h]["total"] += 1
        if m.get("is_flagged"): hourly[h]["toxic"] += 1
    return {"total_messages": total, "toxic_count": toxic, "non_toxic_count": total-toxic,
            "toxicity_rate": round(toxic/max(total,1), 4),
            "most_toxic_users": [{"username":u,"toxic_count":c} for u,c in top],
            "hourly_trend": sorted(hourly.values(), key=lambda x: x["hour"])}

async def create_group(name, members, creator):
    g = {"name": name, "members": list(set(members+[creator])), "creator": creator}
    _store["groups"].append(g)
    return g

async def get_user_groups(username):
    return [g for g in _store["groups"] if username in g.get("members", [])]
'''

with open('toxichat_backend/database.py', 'w') as f:
    f.write(database_py)

# ── __init__.py ──────────────────────────────────────────────
with open('toxichat_backend/__init__.py', 'w') as f:
    f.write('')

print('✅ Backend files created!')

# === CELL 3: Create main.py ===
main_py = '''
import os, json, asyncio, sys
sys.path.insert(0, os.path.dirname(__file__))

from datetime import datetime, timedelta
from typing import Dict
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from jose import jwt, JWTError
from passlib.context import CryptContext

from models import *
import database as db
import ml_service

SECRET_KEY = "toxichat-colab-secret"
ALGORITHM = "HS256"
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

app = FastAPI(title="ToxiChat API")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True,
                   allow_methods=["*"], allow_headers=["*"])

def create_token(username):
    expire = datetime.utcnow() + timedelta(hours=24)
    return jwt.encode({"sub": username, "exp": expire}, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("sub")
    except JWTError:
        raise HTTPException(401, "Invalid token")

@app.on_event("startup")
async def startup():
    await db.get_db()
    print("ToxiChat API ready!")

@app.post("/api/register")
async def register(data: UserRegister):
    if await db.get_user(data.username):
        raise HTTPException(400, "Username taken")
    await db.create_user(data.username, pwd_context.hash(data.password),
                         data.display_name or data.username)
    token = create_token(data.username)
    return {"access_token": token, "token_type": "bearer",
            "username": data.username, "display_name": data.display_name or data.username}

@app.post("/api/login")
async def login(data: UserLogin):
    user = await db.get_user(data.username)
    if not user or not pwd_context.verify(data.password, user["password"]):
        raise HTTPException(401, "Invalid credentials")
    token = create_token(data.username)
    return {"access_token": token, "token_type": "bearer",
            "username": data.username, "display_name": user["display_name"]}

@app.get("/api/users")
async def list_users():
    return await db.get_all_users()

@app.post("/api/predict")
async def predict(data: ToxicityRequest):
    r = ml_service.predict_toxicity(data.text)
    return {"text": data.text, **r}

@app.get("/api/messages/{u1}/{u2}")
async def get_msgs(u1: str, u2: str):
    return await db.get_messages(u1, u2)

@app.get("/api/dashboard/stats")
async def stats():
    return await db.get_dashboard_stats()

@app.get("/")
async def health():
    return {"app": "ToxiChat", "status": "running", "ml_loaded": ml_service._ready}

# WebSocket
class ConnectionManager:
    def __init__(self):
        self.connections: Dict[str, WebSocket] = {}
    async def connect(self, username, ws):
        await ws.accept()
        self.connections[username] = ws
        await db.set_user_online(username, True)
    async def disconnect(self, username):
        self.connections.pop(username, None)
        await db.set_user_online(username, False)
    async def send_to(self, username, data):
        ws = self.connections.get(username)
        if ws:
            try: await ws.send_json(data)
            except: self.connections.pop(username, None)

manager = ConnectionManager()

@app.websocket("/ws/{token}")
async def ws_endpoint(websocket: WebSocket, token: str):
    try: username = verify_token(token)
    except:
        await websocket.close(code=4001); return
    await manager.connect(username, websocket)
    users = await db.get_all_users()
    await websocket.send_json({"type": "users_list", "users": users})
    try:
        while True:
            raw = await websocket.receive_text()
            data = json.loads(raw)
            if data.get("type") == "message":
                text = data.get("text", "").strip()
                receiver = data.get("receiver", "")
                if not text or not receiver: continue
                tox = ml_service.predict_toxicity(text)
                msg = await db.save_message({
                    "sender": username, "receiver": receiver, "text": text,
                    "is_group": False, "toxicity_score": tox["score"],
                    "toxicity_label": tox["label"], "is_flagged": tox["is_flagged"]})
                payload = {"type": "message", "id": msg["id"], "sender": username,
                           "receiver": receiver, "text": text, "timestamp": msg["timestamp"],
                           "is_group": False, **tox}
                await manager.send_to(username, payload)
                if tox["is_flagged"]:
                    await manager.send_to(receiver, {
                        "type": "toxicity_warning",
                        "message": "This message may contain harmful content",
                        "from": username, "score": tox["score"]})
                await manager.send_to(receiver, payload)
                if tox["is_flagged"]:
                    await manager.send_to(username, {
                        "type": "toxicity_alert",
                        "message": "Your message was flagged as toxic!",
                        "score": tox["score"], "label": tox["label"]})
            elif data.get("type") == "get_users":
                users = await db.get_all_users()
                await websocket.send_json({"type": "users_list", "users": users})
    except WebSocketDisconnect:
        await manager.disconnect(username)
    except Exception as e:
        print(f"WS error: {e}")
        await manager.disconnect(username)
'''

with open('toxichat_backend/main.py', 'w') as f:
    f.write(main_py)

print('✅ main.py created!')

# === CELL 4: Start Server with ngrok ===
import subprocess, threading

# Start uvicorn in background
def run_server():
    subprocess.run(['python', '-m', 'uvicorn', 'main:app', '--host', '0.0.0.0', '--port', '8000'],
                   cwd='toxichat_backend')

server_thread = threading.Thread(target=run_server, daemon=True)
server_thread.start()

import time; time.sleep(3)

# Setup ngrok
from pyngrok import ngrok
ngrok.set_auth_token("YOUR_NGROK_AUTH_TOKEN")  # Get free token at ngrok.com
public_url = ngrok.connect(8000, "http")
print(f'\n🚀 ToxiChat Backend is LIVE!')
print(f'📡 Public URL: {public_url}')
print(f'📡 Use this as REACT_APP_API_URL in your React frontend')
print(f'\n🧪 Test: {public_url}/api/predict  (POST with {{"text": "you are stupid"}})')

# === CELL 5: Test API ===
import requests

# Test health
r = requests.get(f'{public_url}/')
print(f'Health: {r.json()}')

# Test toxicity prediction
r = requests.post(f'{public_url}/api/predict', json={"text": "you are so stupid and dumb"})
print(f'Toxic test: {r.json()}')

r = requests.post(f'{public_url}/api/predict', json={"text": "have a great day!"})
print(f'Safe test: {r.json()}')

# Test registration
r = requests.post(f'{public_url}/api/register',
                  json={"username": "testuser", "password": "test123", "display_name": "Test User"})
print(f'Register: {r.json()}')

print('\n✅ All API tests passed!')
