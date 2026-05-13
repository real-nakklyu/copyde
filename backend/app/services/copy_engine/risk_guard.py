from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from app.core.config import Settings, get_settings
from app.schemas.bots import BotSettings


@dataclass(frozen=True)
class RiskContext:
    bot_status: str
    account_environment: str
    symbol: str
    daily_loss: Decimal
    open_positions: int
    total_allocated_margin: Decimal
    quantity: Decimal
    futures_enabled: bool
    account_validated: bool
    user_acknowledged_live_risk: bool
    admin_kill_switch_enabled: bool = False


@dataclass(frozen=True)
class RiskDecision:
    allowed: bool
    reasons: list[str]


def evaluate_risk(settings_json: dict | BotSettings, context: RiskContext, settings: Settings | None = None) -> RiskDecision:
    app_settings = settings or get_settings()
    bot_settings = settings_json if isinstance(settings_json, BotSettings) else BotSettings.model_validate(settings_json)
    reasons: list[str] = []

    if context.bot_status != "running":
        reasons.append("bot is not running")
    if context.admin_kill_switch_enabled:
        reasons.append("admin kill switch is active")
    if app_settings.disable_live_trading:
        reasons.append("DISABLE_LIVE_TRADING is true")
    if context.account_environment == "production" and not app_settings.enable_production_trading:
        reasons.append("production trading is not explicitly enabled")
    if context.account_environment == "production" and app_settings.binance_env != "production":
        reasons.append("backend BINANCE_ENV is not production")
    if not context.user_acknowledged_live_risk or not bot_settings.live_trading_acknowledged:
        reasons.append("live trading risk has not been acknowledged")
    if not context.account_validated or not context.futures_enabled:
        reasons.append("Binance Futures account is not validated for trading")
    if bot_settings.allowed_symbols and context.symbol not in {s.upper() for s in bot_settings.allowed_symbols}:
        reasons.append("symbol is not whitelisted")
    if context.symbol in {s.upper() for s in bot_settings.blocked_symbols}:
        reasons.append("symbol is blacklisted")
    if context.daily_loss >= bot_settings.max_daily_loss:
        reasons.append("daily max loss reached")
    if context.open_positions >= bot_settings.max_open_copied_positions:
        reasons.append("max open copied positions reached")
    if context.total_allocated_margin >= bot_settings.max_total_margin_allocated:
        reasons.append("max total allocated margin reached")
    if context.quantity <= 0:
        reasons.append("quantity is below minimum")

    return RiskDecision(allowed=not reasons, reasons=reasons)

