"""
WebSocket Connection Pool Manager
Dead connection cleaner for telephony calls
"""

import asyncio
from typing import Dict, Optional
from datetime import datetime, timedelta
from fastapi import WebSocket


class ConnectionManager:
    """Manages active WebSocket connections for voice calls"""

    def __init__(self):
        self.active_connections: Dict[str, dict] = {}
        self._cleanup_task: Optional[asyncio.Task] = None

    async def connect(self, call_id: str, websocket: WebSocket):
        """Register new call connection"""
        await websocket.accept()
        self.active_connections[call_id] = {
            "ws": websocket,
            "start_time": datetime.now(),
            "last_activity": datetime.now(),
            "language": "hi"
        }
        print(f"📞 Call connected: {call_id}")

    def disconnect(self, call_id: str):
        """Remove call connection"""
        if call_id in self.active_connections:
            del self.active_connections[call_id]
            print(f"📴 Call disconnected: {call_id}")

    def update_activity(self, call_id: str):
        """Update last activity timestamp"""
        if call_id in self.active_connections:
            self.active_connections[call_id]["last_activity"] = datetime.now()

    async def _cleanup_loop(self):
        """Background task to clean dead connections"""
        while True:
            await asyncio.sleep(60)  # Check every minute
            now = datetime.now()
            dead_calls = []

            for call_id, conn in self.active_connections.items():
                # Kill connections idle for > 5 minutes
                if now - conn["last_activity"] > timedelta(minutes=5):
                    dead_calls.append(call_id)

            for call_id in dead_calls:
                try:
                    conn = self.active_connections[call_id]
                    await conn["ws"].close()
                except:
                    pass
                self.disconnect(call_id)
                print(f"🧹 Cleaned dead connection: {call_id}")

    def start_cleanup(self):
        """Start background cleanup task"""
        if self._cleanup_task is None or self._cleanup_task.done():
            self._cleanup_task = asyncio.create_task(self._cleanup_loop())

    def get_stats(self) -> dict:
        """Return connection statistics"""
        return {
            "active_calls": len(self.active_connections),
            "calls": [
                {
                    "call_id": cid,
                    "duration_seconds": (datetime.now() - conn["start_time"]).seconds,
                    "language": conn["language"]
                }
                for cid, conn in self.active_connections.items()
            ]
        }


# Singleton
manager = ConnectionManager()
