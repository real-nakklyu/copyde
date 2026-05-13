from __future__ import annotations

from typing import Any

from app.core.supabase import SupabaseRestClient


def eq(field: str, value: Any) -> str:
    return f"eq.{value}"


class BaseRepository:
    table: str

    def __init__(self, client: SupabaseRestClient | None = None) -> None:
        self.client = client or SupabaseRestClient()

    async def list(self, params: dict | None = None) -> list[dict]:
        return await self.client.request("GET", self.table, params=params)  # type: ignore[return-value]

    async def get(self, id_: str) -> dict | None:
        rows = await self.list({"id": eq("id", id_), "limit": "1"})
        return rows[0] if rows else None

    async def create(self, payload: dict) -> dict:
        rows = await self.client.request("POST", self.table, json=payload)
        return rows[0] if isinstance(rows, list) and rows else {}

    async def update(self, id_: str, payload: dict) -> dict:
        rows = await self.client.request("PATCH", self.table, params={"id": eq("id", id_)}, json=payload)
        return rows[0] if isinstance(rows, list) and rows else {}


class ProfileRepository(BaseRepository):
    table = "profiles"

    async def me(self, user_id: str) -> dict | None:
        return await self.get(user_id)


class BinanceAccountRepository(BaseRepository):
    table = "binance_accounts"

    async def for_user(self, user_id: str) -> list[dict]:
        return await self.list({"user_id": eq("user_id", user_id), "deleted_at": "is.null", "order": "created_at.desc"})

    async def get_for_user(self, id_: str, user_id: str) -> dict | None:
        rows = await self.list({"id": eq("id", id_), "user_id": eq("user_id", user_id), "deleted_at": "is.null", "limit": "1"})
        return rows[0] if rows else None


class LeaderRepository(BaseRepository):
    table = "leader_profiles"

    async def active(self) -> list[dict]:
        return await self.list({"is_active": "eq.true", "order": "created_at.desc"})


class BotRepository(BaseRepository):
    table = "bots"

    async def for_user(self, user_id: str) -> list[dict]:
        return await self.list({"user_id": eq("user_id", user_id), "order": "created_at.desc"})

    async def get_for_user(self, id_: str, user_id: str) -> dict | None:
        rows = await self.list({"id": eq("id", id_), "user_id": eq("user_id", user_id), "limit": "1"})
        return rows[0] if rows else None

    async def running_for_leader(self, leader_id: str) -> list[dict]:
        return await self.list({"leader_id": eq("leader_id", leader_id), "status": "eq.running", "order": "created_at.asc"})


class TradeSignalRepository(BaseRepository):
    table = "trade_signals"

    async def by_external(self, leader_id: str, external_signal_id: str) -> dict | None:
        rows = await self.list({"leader_id": eq("leader_id", leader_id), "external_signal_id": eq("external_signal_id", external_signal_id), "limit": "1"})
        return rows[0] if rows else None


class CopiedTradeRepository(BaseRepository):
    table = "copied_trades"

    async def for_user(self, user_id: str) -> list[dict]:
        return await self.list({"select": "*,bots!inner(user_id)", "bots.user_id": eq("user_id", user_id), "order": "created_at.desc"})


class CopiedOrderRepository(BaseRepository):
    table = "copied_orders"


class PositionSnapshotRepository(BaseRepository):
    table = "position_snapshots"


class RiskEventRepository(BaseRepository):
    table = "risk_events"


class AuditRepository(BaseRepository):
    table = "audit_logs"


class NotificationRepository(BaseRepository):
    table = "notifications"


class ApiErrorLogRepository(BaseRepository):
    table = "api_error_logs"
