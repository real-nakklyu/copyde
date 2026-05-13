from decimal import Decimal

from app.core.config import Settings
from app.services.copy_engine.copy_executor import LiveTradingDisabledError, ensure_live_order_allowed


def test_emergency_disable_live_trading_blocks_executor():
    try:
        ensure_live_order_allowed("testnet", Settings(DISABLE_LIVE_TRADING=True))
    except LiveTradingDisabledError as exc:
        assert "DISABLE_LIVE_TRADING" in str(exc)
    else:
        raise AssertionError("LiveTradingDisabledError was not raised")

