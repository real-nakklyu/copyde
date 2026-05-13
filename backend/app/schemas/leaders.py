from __future__ import annotations

from pydantic import BaseModel, Field


class LeaderApply(BaseModel):
    display_name: str = Field(min_length=2, max_length=80)
    description: str = Field(min_length=10, max_length=1000)
    binance_account_id: str


class ManualSignalCreate(BaseModel):
    leader_id: str
    external_signal_id: str
    symbol: str
    side: str
    action: str
    entry_type: str = "MARKET"
    price: str | None = None
    quantity: str | None = None
    leverage: int | None = None
    margin_type: str = "isolated"
    position_side: str | None = None
    raw_payload: dict = {}

