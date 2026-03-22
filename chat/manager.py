import json
from typing import Dict, Optional
from fastapi import WebSocket


class ConnectionManager:
    def __init__(self):
        # Maps client_id -> {"ws": WebSocket, "username": str, "role": str}
        self.active_connections: Dict[str, dict] = {}

    async def connect(self, websocket: WebSocket, client_id: str, username: str, role: str):
        await websocket.accept()
        self.active_connections[client_id] = {
            "ws": websocket,
            "username": username,
            "role": role,
        }

    def disconnect(self, client_id: str):
        self.active_connections.pop(client_id, None)

    def get_online_users(self) -> list:
        # Snapshot to avoid mutation issues
        return [
            {"client_id": cid, "username": data["username"], "role": data["role"]}
            for cid, data in list(self.active_connections.items())
        ]

    async def broadcast(self, message: dict, exclude: Optional[str] = None):
        payload = json.dumps(message)
        dead = []
        # Iterate over a SNAPSHOT so disconnects mid-broadcast don't crash
        for cid, data in list(self.active_connections.items()):
            if cid == exclude:
                continue
            try:
                await data["ws"].send_text(payload)
            except Exception:
                dead.append(cid)
        for cid in dead:
            self.disconnect(cid)

    async def broadcast_all(self, message: dict):
        await self.broadcast(message, exclude=None)

    async def send_personal(self, client_id: str, message: dict):
        conn = self.active_connections.get(client_id)
        if conn:
            try:
                await conn["ws"].send_text(json.dumps(message))
            except Exception:
                self.disconnect(client_id)

    async def broadcast_users_update(self):
        await self.broadcast_all({
            "type": "users_update",
            "data": {"users": self.get_online_users()},
        })


manager = ConnectionManager()
