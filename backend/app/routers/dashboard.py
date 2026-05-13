from __future__ import annotations

from decimal import Decimal

from fastapi import APIRouter, Depends

from app.core.auth import AuthenticatedUser, get_current_user
from app.services.supabase.repositories import BotRepository, CopiedTradeRepository, RiskEventRepository

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/summary")
async def summary(user: AuthenticatedUser = Depends(get_current_user)) -> dict:
    bots = await BotRepository().for_user(user.id)
    trades = await CopiedTradeRepository().for_user(user.id)
    risk_events = await RiskEventRepository().list({"select": "*,bots!inner(user_id)", "bots.user_id": f"eq.{user.id}", "order": "created_at.desc", "limit": "20"})
    realized = sum(Decimal(str(t.get("pnl_realized") or 0)) for t in trades)
    open_trades = [t for t in trades if t.get("status") in {"pending", "open", "partially_closed"}]
    allocated = sum(Decimal(str(t.get("follower_margin") or 0)) for t in open_trades)
    return {
        "total_allocated": str(allocated),
        "open_copied_positions": len(open_trades),
        "realized_pnl": str(realized),
        "unrealized_pnl": "0",
        "active_bots": len([b for b in bots if b.get("status") == "running"]),
        "risk_warnings": risk_events,
        "recent_copied_trades": trades[:10],
    }

