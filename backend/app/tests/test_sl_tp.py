from decimal import Decimal

from app.services.binance.exchange_info import SymbolRules
from app.services.copy_engine.sl_tp_manager import stop_loss_price, take_profit_price


RULES = SymbolRules("ETHUSDT", Decimal("0.001"), Decimal("0.001"), Decimal("0.01"), Decimal("5"))


def test_long_sl_tp_percentages():
    assert stop_loss_price(Decimal("100"), "LONG", Decimal("2"), None, RULES) == Decimal("98.00")
    assert take_profit_price(Decimal("100"), "LONG", Decimal("3"), None, RULES) == Decimal("103.00")


def test_short_sl_tp_percentages():
    assert stop_loss_price(Decimal("100"), "SHORT", Decimal("2"), None, RULES) == Decimal("102.00")
    assert take_profit_price(Decimal("100"), "SHORT", Decimal("3"), None, RULES) == Decimal("97.00")

