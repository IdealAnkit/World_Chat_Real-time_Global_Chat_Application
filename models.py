from typing import Optional
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime


# ─── User Models ───────────────────────────────────────────────────────────────

class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=30)
    email: EmailStr
    password: str = Field(..., min_length=6)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: str
    username: str
    email: str
    role: str  # "user" | "admin"


class UserInDB(BaseModel):
    id: Optional[str] = None
    username: str
    email: str
    hashed_password: str
    role: str = "user"


# ─── Token Models ──────────────────────────────────────────────────────────────

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


class TokenData(BaseModel):
    user_id: Optional[str] = None
    username: Optional[str] = None
    role: Optional[str] = None


# ─── Message Models ────────────────────────────────────────────────────────────

class MessageCreate(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)


class MessageOut(BaseModel):
    id: str
    user_id: Optional[str] = None
    username: str
    message: str
    timestamp: str
    is_admin: bool = False
    is_edited: bool = False


class MessageEdit(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)


# ─── WebSocket Payload Models ─────────────────────────────────────────────────

class WSMessage(BaseModel):
    type: str   # "message" | "delete" | "edit" | "typing" | "users_update"
    data: dict
