from __future__ import annotations

import asyncio
import json
from collections.abc import Awaitable, Callable

import websockets

from app.services.binance.futures_client import BinanceFuturesClient


class UserDataStreamRunner:
    def __init__(self, client: BinanceFuturesClient, on_event: Callable[[dict], Awaitable[None]]) -> None:
        self.client = client
        self.on_event = on_event
        self._running = False

    async def run_forever(self) -> None:
        self._running = True
        while self._running:
            listen_key = await self.client.create_listen_key()
            keepalive_task = asyncio.create_task(self._keepalive_loop())
            try:
                async with websockets.connect(f"{self.client.ws_url}/{listen_key}", ping_interval=20, close_timeout=10) as ws:
                    async for message in ws:
                        await self.on_event(json.loads(message))
            finally:
                keepalive_task.cancel()
                await asyncio.sleep(3)

    async def stop(self) -> None:
        self._running = False
        await self.client.close_listen_key()

    async def _keepalive_loop(self) -> None:
        while True:
            await asyncio.sleep(50 * 60)
            await self.client.keepalive_listen_key()

