from __future__ import annotations

from datetime import datetime, timezone

from app.services.supabase.repositories import BotRepository, RiskEventRepository


async def reconcile_active_bots() -> None:
    bots = await BotRepository().list({"status": "eq.running"})
    for bot in bots:
        await BotRepository().update(bot["id"], {"last_heartbeat_at": datetime.now(timezone.utc).isoformat()})
        await RiskEventRepository().create(
            {
                "bot_id": bot["id"],
                "event_type": "reconciliation_checked",
                "severity": "info",
                "message": "Worker reconciliation heartbeat completed; live Binance diff is performed by account-specific runners.",
                "action_taken": "heartbeat",
            }
        )
