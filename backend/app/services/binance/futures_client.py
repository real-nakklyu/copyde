from __future__ import annotations

from typing import Any, Literal

from app.services.binance.base import BinanceBaseClient


class BinanceFuturesClient(BinanceBaseClient):
    async def exchange_info(self) -> dict:
        return await self.request("GET", "/fapi/v1/exchangeInfo")

    async def mark_price(self, symbol: str) -> dict:
        return await self.request("GET", "/fapi/v1/premiumIndex", params={"symbol": symbol})

    async def account(self) -> dict:
        return await self.request("GET", "/fapi/v3/account", signed=True)

    async def balance(self) -> list[dict]:
        return await self.request("GET", "/fapi/v3/balance", signed=True)

    async def position_risk(self, symbol: str | None = None) -> list[dict]:
        params = {"symbol": symbol} if symbol else None
        return await self.request("GET", "/fapi/v3/positionRisk", params=params, signed=True)

    async def position_mode(self) -> dict:
        return await self.request("GET", "/fapi/v1/positionSide/dual", signed=True)

    async def change_leverage(self, symbol: str, leverage: int) -> dict:
        return await self.request("POST", "/fapi/v1/leverage", params={"symbol": symbol, "leverage": leverage}, signed=True)

    async def change_margin_type(self, symbol: str, margin_type: Literal["ISOLATED", "CROSSED"]) -> dict:
        return await self.request("POST", "/fapi/v1/marginType", params={"symbol": symbol, "marginType": margin_type}, signed=True)

    async def new_order(self, **params: Any) -> dict:
        return await self.request("POST", "/fapi/v1/order", params=params, signed=True)

    async def cancel_order(self, symbol: str, order_id: str | None = None, client_order_id: str | None = None) -> dict:
        params: dict[str, Any] = {"symbol": symbol}
        if order_id:
            params["orderId"] = order_id
        if client_order_id:
            params["origClientOrderId"] = client_order_id
        return await self.request("DELETE", "/fapi/v1/order", params=params, signed=True)

    async def create_listen_key(self) -> str:
        payload = await self.request("POST", "/fapi/v1/listenKey", api_key_required=True)
        return payload["listenKey"]

    async def keepalive_listen_key(self) -> dict:
        return await self.request("PUT", "/fapi/v1/listenKey", api_key_required=True)

    async def close_listen_key(self) -> dict:
        return await self.request("DELETE", "/fapi/v1/listenKey", api_key_required=True)

    async def validate_futures_access(self) -> dict[str, Any]:
        account = await self.account()
        can_trade = bool(account.get("canTrade", False))
        return {
            "futures_enabled": can_trade,
            "permissions_detected": {
                "canTrade": can_trade,
                "canDeposit": account.get("canDeposit"),
                "canWithdraw": account.get("canWithdraw"),
                "feeTier": account.get("feeTier"),
                "multiAssetsMargin": account.get("multiAssetsMargin"),
            },
        }

