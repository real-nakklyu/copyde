from decimal import Decimal

from app.services.binance.exchange_info import SymbolRules, ensure_symbol_minimums, round_price, round_quantity


def test_quantity_and_price_round_down_to_binance_filters():
    rules = SymbolRules("BTCUSDT", Decimal("0.001"), Decimal("0.001"), Decimal("0.10"), Decimal("5"))

    assert round_quantity(Decimal("0.123456"), rules) == Decimal("0.123")
    assert round_price(Decimal("65432.198"), rules) == Decimal("65432.10")
    ensure_symbol_minimums(Decimal("0.001"), Decimal("65000"), rules)

