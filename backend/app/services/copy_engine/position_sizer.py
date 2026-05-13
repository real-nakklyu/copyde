from __future__ import annotations

from decimal import Decimal

from app.schemas.bots import BotSettings
from app.services.binance.exchange_info import SymbolRules, ensure_symbol_minimums, round_quantity


def fixed_margin_quantity(margin: Decimal, leverage: int, price: Decimal, rules: SymbolRules) -> Decimal:
    target_notional = margin * Decimal(leverage)
    quantity = round_quantity(target_notional / price, rules)
    ensure_symbol_minimums(quantity, price, rules)
    return quantity


def percentage_balance_margin(balance: Decimal, percent: Decimal, cap: Decimal | None = None) -> Decimal:
    margin = balance * (percent / Decimal("100"))
    return min(margin, cap) if cap is not None else margin


def proportional_notional(
    leader_notional: Decimal,
    leader_equity: Decimal,
    follower_allocated_equity: Decimal,
    cap_notional: Decimal,
) -> Decimal:
    if leader_equity <= 0:
        raise ValueError("Leader equity must be positive for proportional sizing.")
    exposure_ratio = leader_notional / leader_equity
    return min(follower_allocated_equity * exposure_ratio, cap_notional)


def calculate_quantity(
    settings: BotSettings,
    price: Decimal,
    rules: SymbolRules,
    available_balance: Decimal,
    leader_notional: Decimal | None = None,
    leader_equity: Decimal | None = None,
) -> Decimal:
    leverage = min(settings.custom_leverage, settings.max_leverage)
    if settings.allocation_mode == "fixed_margin":
        margin = min(settings.fixed_margin_usdt or Decimal("0"), settings.max_margin_per_trade)
        return fixed_margin_quantity(margin, leverage, price, rules)
    if settings.allocation_mode == "percentage_balance":
        margin = percentage_balance_margin(available_balance, settings.balance_percent or Decimal("0"), settings.max_margin_per_trade)
        return fixed_margin_quantity(margin, leverage, price, rules)
    if leader_notional is None or leader_equity is None:
        raise ValueError("Leader notional and equity are required for proportional sizing.")
    notional = proportional_notional(
        leader_notional,
        leader_equity,
        settings.proportional_equity_cap_usdt or settings.max_total_margin_allocated,
        settings.max_margin_per_trade * Decimal(leverage),
    )
    quantity = round_quantity(notional / price, rules)
    ensure_symbol_minimums(quantity, price, rules)
    return quantity

