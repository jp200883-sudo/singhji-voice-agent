"""
Singh Ji Voice AI — WebSocket Connection Manager
Dead connection cleaner, connection pool
"""

import asyncio
import time
from typing import Dict, Set
from fastapi import WebSocket


class ConnectionManager:
    """
    WebSocket Connection Pool
    - Tracks active connections
    - Auto-removes dead connections
    - Heartbeat/ping support
    """

    def __init__(self, heartbeat_interval: int = 30, max_connections: int = 100):
        self.active_connections: Dict[str, WebSocket] = {}
        self.connection_times: Dict[str, float] = {}
        self.heartbeat_interval = heartbeat_interval
        self.max_connections = max_connections
        self._cleanup_task = None

    async def connect(self, websocket: WebSocket, client_id: str):
        """Accept and track new WebSocket connection"""
        if len(self.active_connections) >= self.max_connections:
            await websocket.close(code=1008, reason="Server full")
            return False

        await websocket.accept()
        self.active_connections[client_id] = websocket
        self.connection_times[client_id] = time.time()
        print(f"🔌 WS Connected: {client_id} (Total: {len(self.active_connections)})")
        return True

    def disconnect(self, client_id: str):
        """Remove connection from pool"""
        if client_id in self.active_connections:
            del self.active_connections[client_id]
            del self.connection_times[client_id]
            print(f"❌ WS Disconnected: {client_id} (Total: {len(self.active_connections)})")

    async def send_text(self, client_id: str, message: str):
        """Send text message to specific client"""
        if client_id in self.active_connections:
            try:
                await self.active_connections[client_id].send_text(message)
            except Exception:
                self.disconnect(client_id)

    async def send_bytes(self, client_id: str, data: bytes):
        """Send binary data to specific client"""
        if client_id in self.active_connections:
            try:
                await self.active_connections[client_id].send_bytes(data)
            except Exception:
                self.disconnect(client_id)

    async def broadcast(self, message: str):
        """Broadcast text to all connected clients"""
        dead = []
        for client_id, ws in self.active_connections.items():
            try:
                await ws.send_text(message)
            except Exception:
                dead.append(client_id)

        for client_id in dead:
            self.disconnect(client_id)

    async def heartbeat(self, client_id: str):
        """Send ping to keep connection alive"""
        if client_id in self.active_connections:
            try:
                await self.active_connections[client_id].send_json({"type": "ping"})
            except Exception:
                self.disconnect(client_id)

    async def start_cleanup(self):
        """Background task to clean dead connections"""
        while True:
            await asyncio.sleep(self.heartbeat_interval)
            await self._cleanup_dead()

    async def _cleanup_dead(self):
        """Remove connections that haven't responded"""
        now = time.time()
        dead = []
        for client_id, conn_time in self.connection_times.items():
            if now - conn_time > self.heartbeat_interval * 3:
                dead.append(client_id)

        for client_id in dead:
            self.disconnect(client_id)
            print(f"🧹 Cleaned dead connection: {client_id}")

    def get_stats(self) -> dict:
        """Get connection pool statistics"""
        return {
            "active_connections": len(self.active_connections),
            "max_connections": self.max_connections,
            "client_ids": list(self.active_connections.keys())
        }


# Global connection manager instance
manager = ConnectionManager()
