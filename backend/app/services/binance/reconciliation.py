from __future__ import annotations

from app.services.binance.futures_client import BinanceFuturesClient


async def build_reconciliation_report(client: BinanceFuturesClient, db_positions: list[dict]) -> dict:
    live_positions = await client.position_risk()
    live_by_key = {(p["symbol"], p.get("positionSide", "BOTH")): p for p in live_positions if float(p.get("positionAmt", "0")) != 0}
    db_by_key = {(p["symbol"], p.get("position_side", "BOTH")): p for p in db_positions}
    orphaned = [value for key, value in live_by_key.items() if key not in db_by_key]
    stale = [value for key, value in db_by_key.items() if key not in live_by_key]
    return {"orphaned_live_positions": orphaned, "stale_database_positions": stale, "auto_fixed": False}

