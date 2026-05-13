from __future__ import annotations

import base64
import hashlib
import hmac
import json
import secrets
from dataclasses import dataclass
from typing import Any
from urllib.parse import urlencode

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from fastapi import HTTPException, Request, status

from app.core.config import Settings, get_settings


SENSITIVE_KEYS = {"api_secret", "apiSecret", "secret", "signature", "authorization", "jwt", "refresh_token"}


def mask_api_key(api_key: str) -> str:
    if len(api_key) <= 10:
        return f"{api_key[:2]}****{api_key[-2:]}"
    return f"{api_key[:6]}****{api_key[-4:]}"


def redact_sensitive(payload: Any) -> Any:
    if isinstance(payload, dict):
        redacted: dict[str, Any] = {}
        for key, value in payload.items():
            redacted[key] = "***REDACTED***" if key.lower() in SENSITIVE_KEYS else redact_sensitive(value)
        return redacted
    if isinstance(payload, list):
        return [redact_sensitive(item) for item in payload]
    return payload


def _load_master_key(settings: Settings) -> bytes:
    raw = settings.encryption_master_key
    if not raw:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="ENCRYPTION_MASTER_KEY is required before storing Binance credentials.",
        )
    try:
        decoded = base64.urlsafe_b64decode(raw + "=" * (-len(raw) % 4))
    except Exception as exc:  # pragma: no cover - defensive
        raise HTTPException(status_code=500, detail="Invalid encryption master key encoding.") from exc
    if len(decoded) not in {16, 24, 32}:
        raise HTTPException(status_code=500, detail="ENCRYPTION_MASTER_KEY must decode to 16, 24, or 32 bytes.")
    return decoded


def encrypt_secret(plaintext: str, settings: Settings | None = None) -> str:
    settings = settings or get_settings()
    aesgcm = AESGCM(_load_master_key(settings))
    nonce = secrets.token_bytes(12)
    ciphertext = aesgcm.encrypt(nonce, plaintext.encode("utf-8"), b"binance-secret-v1")
    return base64.urlsafe_b64encode(nonce + ciphertext).decode("ascii")


def decrypt_secret(token: str, settings: Settings | None = None) -> str:
    settings = settings or get_settings()
    raw = base64.urlsafe_b64decode(token.encode("ascii"))
    nonce, ciphertext = raw[:12], raw[12:]
    plaintext = AESGCM(_load_master_key(settings)).decrypt(nonce, ciphertext, b"binance-secret-v1")
    return plaintext.decode("utf-8")


def sign_binance_params(params: dict[str, Any], secret_key: str) -> str:
    query = urlencode(params, doseq=True)
    return hmac.new(secret_key.encode("utf-8"), query.encode("utf-8"), hashlib.sha256).hexdigest()


@dataclass(slots=True)
class RateLimitBucket:
    count: int
    reset_at: float


class InMemoryRateLimiter:
    def __init__(self) -> None:
        self._buckets: dict[str, RateLimitBucket] = {}

    def check(self, key: str, limit: int, now: float) -> None:
        bucket = self._buckets.get(key)
        if bucket is None or now >= bucket.reset_at:
            self._buckets[key] = RateLimitBucket(count=1, reset_at=now + 60)
            return
        bucket.count += 1
        if bucket.count > limit:
            raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="Rate limit exceeded.")


rate_limiter = InMemoryRateLimiter()


async def rate_limit_dependency(request: Request) -> None:
    import time

    settings = get_settings()
    user = getattr(request.state, "user", None)
    subject = user.id if user else request.client.host if request.client else "anonymous"
    route = request.scope.get("path", "unknown")
    rate_limiter.check(f"{subject}:{route}", settings.rate_limit_per_minute, time.time())


def safe_json(payload: Any) -> str:
    return json.dumps(redact_sensitive(payload), default=str, separators=(",", ":"))

