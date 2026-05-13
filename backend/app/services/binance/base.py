from __future__ import annotations

import asyncio
import time
from typing import Any, Literal

import httpx
from fastapi import HTTPException

from app.core.security import sign_binance_params


BINANCE_USDM_BASE_URLS = {
    "production": "https://fapi.binance.com",
    "testnet": "https://demo-fapi.binance.com",
}
BINANCE_USDM_WS_URLS = {
    "production": "wss://fstream.binance.com/ws",
    "testnet": "wss://fstream.binancefuture.com/ws",
}


class BinanceApiError(RuntimeError):
    def __init__(self, status_code: int, message: str, payload: Any | None = None) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.payload = payload


class BinanceBaseClient:
    def __init__(self, api_key: str, api_secret: str, environment: Literal["testnet", "production"]) -> None:
        self.api_key = api_key
        self.api_secret = api_secret
        self.environment = environment
        self.base_url = BINANCE_USDM_BASE_URLS[environment]
        self.ws_url = BINANCE_USDM_WS_URLS[environment]

    def _headers(self) -> dict[str, str]:
        return {"X-MBX-APIKEY": self.api_key}

    def _signed_params(self, params: dict[str, Any] | None = None) -> dict[str, Any]:
        signed = dict(params or {})
        signed.setdefault("recvWindow", 5000)
        signed["timestamp"] = int(time.time() * 1000)
        signed["signature"] = sign_binance_params(signed, self.api_secret)
        return signed

    async def request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        signed: bool = False,
        api_key_required: bool = False,
    ) -> Any:
        request_params = self._signed_params(params) if signed else params
        headers = self._headers() if signed or api_key_required else {}
        async with httpx.AsyncClient(timeout=20) as client:
            for attempt in range(4):
                response = await client.request(method, f"{self.base_url}{path}", params=request_params, headers=headers)
                if response.status_code in {429, 418}:
                    await asyncio.sleep(min(2**attempt, 8))
                    continue
                if response.status_code >= 400:
                    try:
                        payload = response.json()
                    except Exception:
                        payload = {"msg": response.text}
                    raise BinanceApiError(response.status_code, payload.get("msg", response.text), payload)
                if not response.content:
                    return {}
                return response.json()
        raise HTTPException(status_code=429, detail="Binance rate limit reached; request backed off and failed.")

