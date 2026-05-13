from decimal import Decimal

from app.schemas.bots import BotSettings
from app.services.binance.exchange_info import SymbolRules
from app.services.copy_engine.position_sizer import calculate_quantity, percentage_balance_margin, proportional_notional


def rules():
    return SymbolRules("BTCUSDT", Decimal("0.001"), Decimal("0.001"), Decimal("0.10"), Decimal("5"))


def test_fixed_margin_position_sizing():
    settings = BotSettings(
        allocation_mode="fixed_margin",
        fixed_margin_usdt=Decimal("50"),
        max_margin_per_trade=Decimal("100"),
        max_total_margin_allocated=Decimal("1000"),
        max_daily_loss=Decimal("200"),
        max_open_copied_positions=5,
        custom_leverage=10,
        live_trading_acknowledged=True,
    )

    assert calculate_quantity(settings, Decimal("25000"), rules(), Decimal("1000")) == Decimal("0.020")


def test_percentage_and_proportional_sizing_helpers():
    assert percentage_balance_margin(Decimal("1000"), Decimal("5"), Decimal("40")) == Decimal("40")
    assert proportional_notional(Decimal("2000"), Decimal("10000"), Decimal("500"), Decimal("80")) == Decimal("80")

