from decimal import Decimal


def margin_from_notional(notional: Decimal, leverage: int) -> Decimal:
    if leverage <= 0:
        raise ValueError("Leverage must be positive.")
    return notional / Decimal(leverage)

