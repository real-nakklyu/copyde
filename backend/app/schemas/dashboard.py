from __future__ import annotations

from pydantic import BaseModel


class DashboardSummary(BaseModel):
    total_allocated: str
    open_copied_positions: int
    realized_pnl: str
    unrealized_pnl: str
    active_bots: int
    risk_warnings: list[dict]
    recent_copied_trades: list[dict]

