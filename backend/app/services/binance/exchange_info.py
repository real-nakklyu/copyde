from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, ROUND_DOWN


@dataclass(frozen=True)
class SymbolRules:
    symbol: str
    min_qty: Decimal
    step_size: Decimal
    tick_size: Decimal
    min_notional: Decimal
    max_qty: Decimal | None = None

    @classmethod
    def from_exchange_symbol(cls, payload: dict) -> "SymbolRules":
        filters = {item["filterType"]: item for item in payload.get("filters", [])}
        lot = filters.get("MARKET_LOT_SIZE") or filters.get("LOT_SIZE") or {}
        price = filters.get("PRICE_FILTER") or {}
        notional = filters.get("MIN_NOTIONAL") or {}
        return cls(
            symbol=payload["symbol"],
            min_qty=Decimal(str(lot.get("minQty", "0"))),
            step_size=Decimal(str(lot.get("stepSize", "1"))),
            tick_size=Decimal(str(price.get("tickSize", "0.01"))),
            min_notional=Decimal(str(notional.get("notional", "0"))),
            max_qty=Decimal(str(lot["maxQty"])) if lot.get("maxQty") else None,
        )


def round_to_step(value: Decimal, step: Decimal) -> Decimal:
    if step == 0:
        return value
    return (value / step).to_integral_value(rounding=ROUND_DOWN) * step


def round_quantity(quantity: Decimal, rules: SymbolRules) -> Decimal:
    return round_to_step(quantity, rules.step_size)


def round_price(price: Decimal, rules: SymbolRules) -> Decimal:
    return round_to_step(price, rules.tick_size)


def ensure_symbol_minimums(quantity: Decimal, price: Decimal, rules: SymbolRules) -> None:
    if quantity < rules.min_qty:
        raise ValueError(f"{rules.symbol} quantity {quantity} is below min quantity {rules.min_qty}.")
    if rules.max_qty is not None and quantity > rules.max_qty:
        raise ValueError(f"{rules.symbol} quantity {quantity} is above max quantity {rules.max_qty}.")
    notional = quantity * price
    if notional < rules.min_notional:
        raise ValueError(f"{rules.symbol} notional {notional} is below minimum notional {rules.min_notional}.")

