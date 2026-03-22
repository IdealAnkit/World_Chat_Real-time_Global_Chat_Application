import json
import uuid
from datetime import datetime, timezone
from typing import Optional

from bson import ObjectId
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException, status, Query

from auth.dependencies import get_current_user, require_admin
from auth.utils import decode_access_token
from chat.manager import manager
from chat.moderation import filter_message
from database import get_messages_collection, get_users_collection
from models import MessageEdit

router = APIRouter(tags=["chat"])


def _msg_out(doc: dict) -> dict:
    return {
        "id": str(doc["_id"]),
        "user_id": str(doc.get("user_id")) if doc.get("user_id") else None,
        "username": doc["username"],
        "message": doc["message"],
        "timestamp": doc["timestamp"],
        "is_admin": doc.get("is_admin", False),
        "is_edited": doc.get("is_edited", False),
    }


# ─── REST: Get history ────────────────────────────────────────────────────────
@router.get("/messages")
async def get_messages(limit: int = Query(50, le=100)):
    collection = get_messages_collection()
    cursor = collection.find().sort("timestamp", -1).limit(limit)
    messages = []
    async for doc in cursor:
        messages.append(_msg_out(doc))
    messages.reverse()
    return messages


# ─── REST: Delete message ─────────────────────────────────────────────────────
@router.delete("/messages/{message_id}")
async def delete_message(
    message_id: str,
    current_user=Depends(get_current_user),
):
    collection = get_messages_collection()
    try:
        oid = ObjectId(message_id)
    except Exception:
        raise HTTPException(400, "Invalid message ID")

    msg = await collection.find_one({"_id": oid})
    if not msg:
        raise HTTPException(404, "Message not found")

    user_id = str(current_user["_id"])
    is_admin = current_user.get("role") == "admin"
    is_owner = msg.get("user_id") and str(msg["user_id"]) == user_id

    if not is_admin and not is_owner:
        raise HTTPException(403, "Not allowed to delete this message")

    await collection.delete_one({"_id": oid})

    # Broadcast delete event
    await manager.broadcast_all({
        "type": "delete_message",
        "data": {"id": message_id},
    })
    return {"detail": "Message deleted"}


# ─── REST: Edit message (admin only) ─────────────────────────────────────────
@router.patch("/messages/{message_id}")
async def edit_message(
    message_id: str,
    body: MessageEdit,
    _admin=Depends(require_admin),
):
    collection = get_messages_collection()
    try:
        oid = ObjectId(message_id)
    except Exception:
        raise HTTPException(400, "Invalid message ID")

    msg = await collection.find_one({"_id": oid})
    if not msg:
        raise HTTPException(404, "Message not found")

    filtered = filter_message(body.message)
    await collection.update_one(
        {"_id": oid},
        {"$set": {"message": filtered, "is_edited": True}},
    )
    updated = await collection.find_one({"_id": oid})
    out = _msg_out(updated)

    await manager.broadcast_all({
        "type": "edit_message",
        "data": out,
    })
    return out


# ─── WebSocket ────────────────────────────────────────────────────────────────
@router.websocket("/ws/{client_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    client_id: str,
    token: Optional[str] = Query(None),
    guest_name: Optional[str] = Query(None),
):
    # Resolve identity
    username = f"Guest_{client_id[:6].upper()}"
    role = "guest"
    user_id = None

    if token:
        payload = decode_access_token(token)
        if payload:
            username = payload.get("username", username)
            role = payload.get("role", "user")
            user_id = payload.get("sub")

    if guest_name:
        username = guest_name

    await manager.connect(websocket, client_id, username, role)

    # Announce join
    await manager.broadcast_all({
        "type": "system",
        "data": {"message": f"👋 {username} joined the chat", "username": "System"},
    })
    await manager.broadcast_users_update()

    try:
        while True:
            raw = await websocket.receive_text()
            try:
                payload_ws = json.loads(raw)
            except json.JSONDecodeError:
                continue

            msg_type = payload_ws.get("type")

            if msg_type == "message":
                text = payload_ws.get("message", "").strip()
                if not text:
                    continue
                filtered = filter_message(text)
                now = datetime.now(timezone.utc).isoformat()

                doc = {
                    "user_id": ObjectId(user_id) if user_id else None,
                    "username": username,
                    "message": filtered,
                    "timestamp": now,
                    "is_admin": role == "admin",
                    "is_edited": False,
                }
                collection = get_messages_collection()
                result = await collection.insert_one(doc)
                doc["_id"] = result.inserted_id

                await manager.broadcast_all({
                    "type": "new_message",
                    "data": _msg_out(doc),
                })

            elif msg_type == "typing":
                await manager.broadcast({
                    "type": "typing",
                    "data": {"username": username},
                }, exclude=client_id)

    except WebSocketDisconnect:
        manager.disconnect(client_id)
        await manager.broadcast_all({
            "type": "system",
            "data": {"message": f"👋 {username} left the chat", "username": "System"},
        })
        await manager.broadcast_users_update()
