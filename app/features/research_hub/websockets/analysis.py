from fastapi import WebSocket, WebSocketDisconnect, HTTPException
from typing import Dict, Set
import logging
import json
from app.core.auth import get_current_user_ws

logger = logging.getLogger(__name__)

class AnalysisNotificationManager:
    def __init__(self):
        self.active_connections: Dict[str, Set[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, task_id: str):
        """Connect a client to a specific task's updates."""
        await websocket.accept()
        if task_id not in self.active_connections:
            self.active_connections[task_id] = set()
        self.active_connections[task_id].add(websocket)
        logger.info(f"Client connected to task {task_id}")

    def disconnect(self, websocket: WebSocket, task_id: str):
        """Disconnect a client from a task's updates."""
        if task_id in self.active_connections:
            self.active_connections[task_id].discard(websocket)
            if not self.active_connections[task_id]:
                del self.active_connections[task_id]
        logger.info(f"Client disconnected from task {task_id}")

    async def notify_update(self, task_id: str, data: dict):
        """Send an update to all clients connected to a task."""
        if task_id not in self.active_connections:
            return

        message = json.dumps(data)
        disconnected = set()

        for connection in self.active_connections[task_id]:
            try:
                await connection.send_text(message)
            except WebSocketDisconnect:
                disconnected.add(connection)
            except Exception as e:
                logger.error(f"Error sending update to client: {str(e)}")
                disconnected.add(connection)

        # Clean up disconnected clients
        for connection in disconnected:
            self.disconnect(connection, task_id)

# Global notification manager
notification_manager = AnalysisNotificationManager() 