import json
from typing import AsyncGenerator
import asyncpg
from ..core.config import settings

async def get_notification_connection() -> asyncpg.Connection:
    """Create a dedicated connection for PostgreSQL notifications."""
    return await asyncpg.connect(
        user=settings.DEV_DB_USER,
        password=settings.DEV_DB_PASSWORD,
        database=settings.DEV_DB_NAME,
        host=settings.DB_HOST,
        port=settings.DB_PORT
    )

async def notify_insight_update(conn: asyncpg.Connection, task_id: str, payload: dict) -> None:
    """Send a notification about an insight update."""
    channel = f"insight_updates_{task_id}"
    await conn.execute(
        "SELECT pg_notify($1, $2)",
        channel,
        json.dumps(payload)
    )

async def listen_insight_updates(task_id: str) -> AsyncGenerator[dict, None]:
    """Listen for insight updates for a specific task."""
    conn = await get_notification_connection()
    channel = f"insight_updates_{task_id}"
    
    try:
        # Start listening
        await conn.add_listener(channel, lambda *args: None)
        
        while True:
            # Wait for notifications
            notification = await conn.wait_for_notify()
            if notification.channel == channel:
                try:
                    payload = json.loads(notification.payload)
                    yield payload
                except json.JSONDecodeError:
                    continue
    finally:
        await conn.remove_listener(channel, lambda *args: None)
        await conn.close() 