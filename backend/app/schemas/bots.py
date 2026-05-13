from __future__ import annotations

from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, Field, model_validator


class BotSettings(BaseModel):
    allocation_mode: Literal["fixed_margin", "percentage_balance", "proportional"]
    fixed_margin_usdt: Decimal | None = None
    balance_percent: Decimal | None = None
    proportional_equity_cap_usdt: Decimal | None = None
    max_margin_per_trade: Decimal
    max_total_margin_allocated: Decimal
    max_daily_loss: Decimal
    max_open_copied_positions: int = Field(ge=1)
    allowed_symbols: list[str] = []
    blocked_symbols: list[str] = []
    slippage_tolerance_percent: Decimal = Decimal("0.5")
    cooldown_after_failed_order_seconds: int = 60
    leverage_mode: Literal["custom", "copy_leader_capped"] = "custom"
    custom_leverage: int = Field(default=5, ge=1)
    max_leverage: int = Field(default=20, ge=1)
    margin_type: Literal["isolated", "cross"] = "isolated"
    stop_loss_percent: Decimal | None = None
    stop_loss_price: Decimal | None = None
    trailing_stop: bool = False
    take_profit_percent: Decimal | None = None
    take_profit_price: Decimal | None = None
    partial_take_profit_percent: Decimal | None = None
    close_behavior: Literal["leader_close", "sl_tp_only", "leader_or_sl_tp"] = "leader_or_sl_tp"
    sync_open_positions: bool = False
    copy_increases: bool = True
    close_if_sltp_fails: bool = True
    live_trading_acknowledged: bool = False

    @model_validator(mode="after")
    def validate_allocation(self) -> "BotSettings":
        if self.allocation_mode == "fixed_margin" and not self.fixed_margin_usdt:
            raise ValueError("fixed_margin_usdt is required for fixed allocation.")
        if self.allocation_mode == "percentage_balance" and not self.balance_percent:
            raise ValueError("balance_percent is required for percentage allocation.")
        if self.allocation_mode == "proportional" and not self.proportional_equity_cap_usdt:
            raise ValueError("proportional_equity_cap_usdt is required for proportional allocation.")
        return self


class BotCreate(BaseModel):
    leader_id: str
    binance_account_id: str
    settings: BotSettings


class BotUpdateSettings(BaseModel):
    settings: BotSettings

