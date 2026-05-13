from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4


def leader_order_to_signal(leader_id: str, event: dict) -> dict | None:
    order = event.get("o") or {}
    status = order.get("X")
    execution_type = order.get("x")
    if execution_type != "TRADE" or status not in {"FILLED", "PARTIALLY_FILLED"}:
        return None
    side = "LONG" if order.get("S") == "BUY" else "SHORT"
    action = "OPEN" if not bool(order.get("R")) else "CLOSE"
    return {
        "leader_id": leader_id,
        "external_signal_id": str(order.get("c") or order.get("i") or uuid4()),
        "symbol": order["s"],
        "side": side,
        "action": action,
        "entry_type": order.get("o", "MARKET"),
        "price": order.get("ap") or order.get("p"),
        "quantity": order.get("l") or order.get("q"),
        "leverage": None,
        "margin_type": "isolated",
        "position_side": order.get("ps"),
        "raw_payload": event,
        "event_time": datetime.fromtimestamp((event.get("E") or 0) / 1000, tz=timezone.utc).isoformat(),
    }

