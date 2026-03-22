from fastapi import APIRouter, HTTPException, status
from bson import ObjectId
from database import get_users_collection
from models import UserCreate, UserLogin, UserOut, Token
from auth.utils import hash_password, verify_password, create_access_token
import re

router = APIRouter(prefix="/auth", tags=["auth"])


def _user_out(user) -> UserOut:
    return UserOut(
        id=str(user["_id"]),
        username=user["username"],
        email=user["email"],
        role=user.get("role", "user"),
    )


@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate):
    users = get_users_collection()

    # Validate username – alphanumeric + underscore only
    if not re.match(r"^[a-zA-Z0-9_]{3,30}$", user_data.username):
        raise HTTPException(400, "Username must be 3-30 alphanumeric characters")

    # Check duplicates
    if await users.find_one({"email": user_data.email}):
        raise HTTPException(400, "Email already registered")
    if await users.find_one({"username": user_data.username}):
        raise HTTPException(400, "Username already taken")

    new_user = {
        "username": user_data.username,
        "email": user_data.email,
        "hashed_password": hash_password(user_data.password),
        "role": "user",
    }
    result = await users.insert_one(new_user)
    new_user["_id"] = result.inserted_id

    token = create_access_token({
        "sub": str(result.inserted_id),
        "username": user_data.username,
        "role": "user",
    })
    return Token(access_token=token, user=_user_out(new_user))


@router.post("/login", response_model=Token)
async def login(credentials: UserLogin):
    users = get_users_collection()
    user = await users.find_one({"email": credentials.email})
    if not user or not verify_password(credentials.password, user["hashed_password"]):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid email or password")

    token = create_access_token({
        "sub": str(user["_id"]),
        "username": user["username"],
        "role": user.get("role", "user"),
    })
    return Token(access_token=token, user=_user_out(user))


@router.get("/me", response_model=UserOut)
async def get_me(credentials: str = None):
    # Handled by JS client using stored token
    raise HTTPException(501, "Use client-side token decoding")
