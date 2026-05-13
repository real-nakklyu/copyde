from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class BinanceAccountCreate(BaseModel):
    label: str = Field(min_length=1, max_length=80)
    api_key: str = Field(min_length=8)
    api_secret: str = Field(min_length=8)
    environment: Literal["testnet", "production"] = "testnet"
    ip_restricted_confirmed: bool = False


class BinanceAccountOut(BaseModel):
    id: str
    label: str
    api_key_masked: str
    environment: Literal["testnet", "production"]
    permissions_detected: dict | None = None
    futures_enabled: bool
    ip_restricted_confirmed: bool
    last_validated_at: datetime | None = None


class BinanceValidationOut(BaseModel):
    valid: bool
    futures_enabled: bool
    permissions_detected: dict
    message: str

