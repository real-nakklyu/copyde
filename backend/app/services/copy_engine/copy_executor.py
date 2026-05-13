from __future__ import annotations

from decimal import Decimal

from app.core.config import Settings, get_settings
from app.schemas.bots import BotSettings
from app.services.binance.exchange_info import SymbolRules
from app.services.binance.futures_client import BinanceFuturesClient
from app.services.binance.order_builder import (
    MarketOrderPlan,
    build_market_order,
    build_stop_market,
    build_take_profit_market,
    client_order_id,
)
from app.services.copy_engine.position_sizer import calculate_quantity
from app.services.copy_engine.sl_tp_manager import close_side_for_position, stop_loss_price, take_profit_price


class LiveTradingDisabledError(RuntimeError):
    pass


def ensure_live_order_allowed(account_environment: str, settings: Settings | None = None) -> None:
    app_settings = settings or get_settings()
    if app_settings.disable_live_trading:
        raise LiveTradingDisabledError("DISABLE_LIVE_TRADING=true prevents live order placement.")
    if account_environment == "production" and not app_settings.enable_production_trading:
        raise LiveTradingDisabledError("ENABLE_PRODUCTION_TRADING must be true for production orders.")


async def execute_open_signal(
    *,
    client: BinanceFuturesClient,
    bot_id: str,
    copied_trade_id: str,
    signal: dict,
    bot_settings: BotSettings,
    rules: SymbolRules,
    available_balance: Decimal,
    hedge_mode: bool,
    settings: Settings | None = None,
) -> dict:
    ensure_live_order_allowed(client.environment, settings)
    symbol = signal["symbol"].upper()
    price = Decimal(str(signal.get("price") or (await client.mark_price(symbol))["markPrice"]))
    quantity = calculate_quantity(bot_settings, price, rules, available_balance)
    leader_leverage = signal.get("leverage") or bot_settings.custom_leverage
    leverage = min(leader_leverage if bot_settings.leverage_mode == "copy_leader_capped" else bot_settings.custom_leverage, bot_settings.max_leverage)
    await client.change_leverage(symbol, leverage)
    await client.change_margin_type(symbol, "ISOLATED" if bot_settings.margin_type == "isolated" else "CROSSED")

    side = "BUY" if signal["side"] == "LONG" else "SELL"
    position_side = signal.get("position_side") or signal["side"]
    entry_order = await client.new_order(
        **build_market_order(
            MarketOrderPlan(
                symbol=symbol,
                side=side,
                position_side=position_side,
                quantity=quantity,
                client_order_id=client_order_id("copyde", copied_trade_id, "entry"),
            ),
            hedge_mode,
        )
    )
    avg_price = Decimal(str(entry_order.get("avgPrice") or price))
    close_side = close_side_for_position(signal["side"])
    sl_price = stop_loss_price(avg_price, signal["side"], bot_settings.stop_loss_percent, bot_settings.stop_loss_price, rules)
    tp_price = take_profit_price(avg_price, signal["side"], bot_settings.take_profit_percent, bot_settings.take_profit_price, rules)
    protective_orders: list[dict] = []
    try:
        if sl_price:
            protective_orders.append(
                await client.new_order(
                    **build_stop_market(symbol, close_side, position_side, sl_price, client_order_id("copyde", copied_trade_id, "sl"), hedge_mode)
                )
            )
        if tp_price:
            protective_orders.append(
                await client.new_order(
                    **build_take_profit_market(symbol, close_side, position_side, tp_price, client_order_id("copyde", copied_trade_id, "tp"), hedge_mode)
                )
            )
    except Exception:
        if bot_settings.close_if_sltp_fails:
            await client.new_order(
                **build_market_order(
                    MarketOrderPlan(
                        symbol=symbol,
                        side=close_side,
                        position_side=position_side,
                        quantity=quantity,
                        client_order_id=client_order_id("copyde", copied_trade_id, "sltp_fail_close"),
                        reduce_only=True,
                    ),
                    hedge_mode,
                )
            )
        raise
    return {"entry_order": entry_order, "protective_orders": protective_orders, "quantity": str(quantity), "entry_price": str(avg_price)}

