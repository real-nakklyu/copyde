from __future__ import annotations

from decimal import Decimal

from app.services.binance.exchange_info import SymbolRules, round_price


def stop_loss_price(entry: Decimal, side: str, percent: Decimal | None, fixed: Decimal | None, rules: SymbolRules) -> Decimal | None:
    if fixed is not None:
        return round_price(fixed, rules)
    if percent is None:
        return None
    if side == "LONG":
        return round_price(entry * (Decimal("1") - percent / Decimal("100")), rules)
    return round_price(entry * (Decimal("1") + percent / Decimal("100")), rules)


def take_profit_price(entry: Decimal, side: str, percent: Decimal | None, fixed: Decimal | None, rules: SymbolRules) -> Decimal | None:
    if fixed is not None:
        return round_price(fixed, rules)
    if percent is None:
        return None
    if side == "LONG":
        return round_price(entry * (Decimal("1") + percent / Decimal("100")), rules)
    return round_price(entry * (Decimal("1") - percent / Decimal("100")), rules)


def close_side_for_position(side: str) -> str:
    return "SELL" if side == "LONG" else "BUY"

