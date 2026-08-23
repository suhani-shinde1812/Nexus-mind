"""
WebSocket endpoint for the real-time layer. Browsers can't set the
Authorization header on the WS handshake, so the JWT access token is passed
as a query param instead: wss://.../ws?token=<access_token>
"""
from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.deps import get_user_from_token
from app.services.realtime import manager

router = APIRouter(tags=["realtime"])


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, token: str = Query(...)):
    db: Session = SessionLocal()
    try:
        user = get_user_from_token(token, db)
    finally:
        db.close()

    if not user:
        await websocket.close(code=4401)
        return

    await manager.connect(websocket)
    try:
        while True:
            # We don't require inbound messages for this app (server -> client
            # fanout only), but we still need to await recv to detect
            # disconnects and to allow future client->server messages
            # (e.g. typing indicators, presence pings) without a protocol change.
            await websocket.receive_text()
    except WebSocketDisconnect:
        pass
    finally:
        manager.disconnect(websocket)
