from __future__ import annotations

import asyncio
import json

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter(tags=["websocket"])


@router.websocket("/ws/dashboard")
async def dashboard_ws(websocket: WebSocket) -> None:
    await websocket.accept()
    try:
        while True:
            await websocket.send_text(json.dumps({"type": "heartbeat"}))
            await asyncio.sleep(15)
    except WebSocketDisconnect:
        return


@router.websocket("/ws/bots/{bot_id}")
async def bot_ws(websocket: WebSocket, bot_id: str) -> None:
    await websocket.accept()
    try:
        while True:
            await websocket.send_text(json.dumps({"type": "heartbeat", "bot_id": bot_id}))
            await asyncio.sleep(15)
    except WebSocketDisconnect:
        return

