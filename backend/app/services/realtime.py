"""
Real-time layer: WebSocket connection manager fanned out through Redis
pub/sub, with automatic local-broadcast fallback if Redis is unavailable.
"""
from __future__ import annotations

import asyncio
import json
import logging

from fastapi import WebSocket
from redis.asyncio import Redis

from app.config import get_settings

logger = logging.getLogger("nexusmind.realtime")
settings = get_settings()


class ConnectionManager:
    def __init__(self) -> None:
        self._connections: set[WebSocket] = set()
        self._redis: Redis | None = None
        self._pubsub_task: asyncio.Task | None = None

    async def startup(self) -> None:
        try:
            r = Redis.from_url(settings.redis_url, decode_responses=True, socket_connect_timeout=0.5)
            await asyncio.wait_for(r.ping(), timeout=0.5)
            self._redis = r
            self._pubsub_task = asyncio.create_task(self._listen())
        except Exception:
            self._redis = None
            logger.info("Redis not available; running in local in-memory broadcast mode.")

    async def shutdown(self) -> None:
        if self._pubsub_task:
            self._pubsub_task.cancel()
        if self._redis:
            try:
                await self._redis.close()
            except Exception:
                pass

    async def connect(self, ws: WebSocket) -> None:
        await ws.accept()
        self._connections.add(ws)

    def disconnect(self, ws: WebSocket) -> None:
        self._connections.discard(ws)

    async def publish(self, event_type: str, payload: dict) -> None:
        """Publish event to Redis or local in-memory fallback."""
        message = json.dumps({"type": event_type, "payload": payload})
        if self._redis is None:
            await self._broadcast_local(message)
            return
        try:
            await self._redis.publish(settings.redis_events_channel, message)
        except Exception:
            await self._broadcast_local(message)

    async def _listen(self) -> None:
        if not self._redis:
            return
        pubsub = self._redis.pubsub()
        try:
            await pubsub.subscribe(settings.redis_events_channel)
            async for message in pubsub.listen():
                if message["type"] != "message":
                    continue
                await self._broadcast_local(message["data"])
        except asyncio.CancelledError:
            pass
        except Exception:
            logger.warning("Redis pub/sub disconnected; falling back to local broadcast.")
        finally:
            try:
                await pubsub.unsubscribe(settings.redis_events_channel)
            except Exception:
                pass

    async def _broadcast_local(self, raw_message: str) -> None:
        dead: list[WebSocket] = []
        for ws in list(self._connections):
            try:
                await ws.send_text(raw_message)
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.disconnect(ws)


manager = ConnectionManager()
