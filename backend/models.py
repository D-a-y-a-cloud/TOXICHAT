"""
Pydantic models for the ToxiChat API.
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


# ── Auth Models ──────────────────────────────────────────────
class UserRegister(BaseModel):
    username: str = Field(..., min_length=3, max_length=30)
    password: str = Field(..., min_length=4)
    display_name: Optional[str] = None


class UserLogin(BaseModel):
    username: str
    password: str


class UserOut(BaseModel):
    username: str
    display_name: str
    created_at: str
    is_online: bool = False


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    username: str
    display_name: str


# ── Message Models ───────────────────────────────────────────
class MessageIn(BaseModel):
    text: str
    receiver: str  # username or group name
    is_group: bool = False


class MessageOut(BaseModel):
    id: str
    sender: str
    receiver: str
    text: str
    timestamp: str
    is_group: bool = False
    toxicity_score: float = 0.0
    toxicity_label: str = "non-toxic"
    is_flagged: bool = False


# ── Toxicity Models ──────────────────────────────────────────
class ToxicityRequest(BaseModel):
    text: str


class ToxicityResult(BaseModel):
    text: str
    score: float
    label: str
    is_flagged: bool


# ── Dashboard Models ─────────────────────────────────────────
class DashboardStats(BaseModel):
    total_messages: int
    toxic_count: int
    non_toxic_count: int
    toxicity_rate: float
    most_toxic_users: List[dict]
    hourly_trend: List[dict]


# ── Group Models ─────────────────────────────────────────────
class GroupCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=50)
    members: List[str]  # list of usernames
