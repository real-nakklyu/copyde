from __future__ import annotations

from decimal import Decimal

from app.services.binance.futures_client import BinanceFuturesClient
from app.services.binance.order_builder import MarketOrderPlan, build_market_order, client_order_id
from app.services.copy_engine.copy_executor import ensure_live_order_allowed
from app.services.copy_engine.sl_tp_manager import close_side_for_position


async def close_copied_position(
    client: BinanceFuturesClient,
    copied_trade_id: str,
    symbol: str,
    side: str,
    position_side: str,
    quantity: Decimal,
    hedge_mode: bool,
) -> dict:
    ensure_live_order_allowed(client.environment)
    return await client.new_order(
        **build_market_order(
            MarketOrderPlan(
                symbol=symbol,
                side=close_side_for_position(side),
                position_side=position_side,
                quantity=quantity,
                client_order_id=client_order_id("copyde", copied_trade_id, "close"),
                reduce_only=True,
            ),
            hedge_mode,
        )
    )

