from __future__ import annotations

from app.services.supabase.repositories import BotRepository, RiskEventRepository


async def monitor_risk() -> None:
    bots = await BotRepository().list({"status": "eq.running"})
    for bot in bots:
        settings = bot.get("settings_json") or {}
        if not settings.get("live_trading_acknowledged"):
            await BotRepository().update(bot["id"], {"status": "paused", "error_message": "Live trading acknowledgement missing during risk monitor."})
            await RiskEventRepository().create(
                {
                    "bot_id": bot["id"],
                    "event_type": "risk_limit_triggered",
                    "severity": "critical",
                    "message": "Bot paused because live trading acknowledgement is missing.",
                    "action_taken": "paused_bot",
                }
            )
