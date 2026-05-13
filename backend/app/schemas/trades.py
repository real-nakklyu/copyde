from __future__ import annotations

from decimal import Decimal

from pydantic import BaseModel


class TradeSignalIn(BaseModel):
    leader_id: str
    external_signal_id: str
    symbol: str
    side: str
    action: str
    entry_type: str = "MARKET"
    price: Decimal | None = None
    quantity: Decimal | None = None
    leverage: int | None = None
    margin_type: str = "isolated"
    position_side: str | None = None
    raw_payload: dict = {}

