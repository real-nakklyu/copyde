import pytest

from app.services.copy_engine.signal_normalizer import leader_order_to_signal


def test_leader_order_signal_has_stable_external_id():
    event = {"E": 1000, "o": {"x": "TRADE", "X": "FILLED", "S": "BUY", "s": "BTCUSDT", "c": "leader-order-1", "q": "0.01", "p": "100"}}

    first = leader_order_to_signal("leader-1", event)
    second = leader_order_to_signal("leader-1", event)

    assert first is not None
    assert first["external_signal_id"] == second["external_signal_id"] == "leader-order-1"

