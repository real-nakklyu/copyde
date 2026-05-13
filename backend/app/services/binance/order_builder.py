from __future__ import annotations

import re
from dataclasses import dataclass
from decimal import Decimal

from app.services.binance.exchange_info import SymbolRules, round_price, round_quantity


CLIENT_ID_RE = re.compile(r"[^.A-Z:/a-z0-9_-]")


def client_order_id(prefix: str, entity_id: str, action: str) -> str:
    raw = f"{prefix}:{entity_id[:18]}:{action}"
    return CLIENT_ID_RE.sub("_", raw)[:36]


@dataclass(frozen=True)
class MarketOrderPlan:
    symbol: str
    side: str
    position_side: str
    quantity: Decimal
    client_order_id: str
    reduce_only: bool = False


def build_market_order(plan: MarketOrderPlan, hedge_mode: bool) -> dict:
    params = {
        "symbol": plan.symbol,
        "side": plan.side,
        "type": "MARKET",
        "quantity": str(plan.quantity.normalize()),
        "newClientOrderId": plan.client_order_id,
        "newOrderRespType": "RESULT",
    }
    if hedge_mode:
        params["positionSide"] = plan.position_side
    else:
        params["positionSide"] = "BOTH"
        if plan.reduce_only:
            params["reduceOnly"] = "true"
    return params


def build_stop_market(symbol: str, close_side: str, position_side: str, stop_price: Decimal, cid: str, hedge_mode: bool) -> dict:
    params = {
        "symbol": symbol,
        "side": close_side,
        "type": "STOP_MARKET",
        "stopPrice": str(stop_price.normalize()),
        "closePosition": "true",
        "workingType": "MARK_PRICE",
        "newClientOrderId": cid,
    }
    if hedge_mode:
        params["positionSide"] = position_side
    return params


def build_take_profit_market(symbol: str, close_side: str, position_side: str, stop_price: Decimal, cid: str, hedge_mode: bool) -> dict:
    params = build_stop_market(symbol, close_side, position_side, stop_price, cid, hedge_mode)
    params["type"] = "TAKE_PROFIT_MARKET"
    return params


def normalize_order_quantity(quantity: Decimal, rules: SymbolRules) -> Decimal:
    return round_quantity(quantity, rules)


def normalize_order_price(price: Decimal, rules: SymbolRules) -> Decimal:
    return round_price(price, rules)

