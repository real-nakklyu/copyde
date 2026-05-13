from decimal import Decimal

from app.core.config import Settings
from app.schemas.bots import BotSettings
from app.services.copy_engine.risk_guard import RiskContext, evaluate_risk


def base_settings():
    return BotSettings(
        allocation_mode="fixed_margin",
        fixed_margin_usdt=Decimal("50"),
        max_margin_per_trade=Decimal("100"),
        max_total_margin_allocated=Decimal("500"),
        max_daily_loss=Decimal("100"),
        max_open_copied_positions=2,
        allowed_symbols=["BTCUSDT"],
        blocked_symbols=["DOGEUSDT"],
        live_trading_acknowledged=True,
    )


def test_production_disabled_by_default_blocks_trade():
    ctx = RiskContext("running", "production", "BTCUSDT", Decimal("0"), 0, Decimal("0"), Decimal("1"), True, True, True)
    decision = evaluate_risk(base_settings(), ctx, Settings(DISABLE_LIVE_TRADING=True, ENABLE_PRODUCTION_TRADING=False))

    assert not decision.allowed
    assert "DISABLE_LIVE_TRADING is true" in decision.reasons
    assert "production trading is not explicitly enabled" in decision.reasons


def test_risk_guard_blocks_symbol_and_open_position_limits():
    ctx = RiskContext("running", "testnet", "ETHUSDT", Decimal("0"), 2, Decimal("0"), Decimal("1"), True, True, True)
    decision = evaluate_risk(base_settings(), ctx, Settings(DISABLE_LIVE_TRADING=False, BINANCE_ENV="testnet"))

    assert not decision.allowed
    assert "symbol is not whitelisted" in decision.reasons
    assert "max open copied positions reached" in decision.reasons

