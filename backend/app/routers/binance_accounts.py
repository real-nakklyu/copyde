from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Request

from app.core.auth import AuthenticatedUser, get_current_user
from app.core.security import decrypt_secret, encrypt_secret, mask_api_key, rate_limit_dependency
from app.schemas.binance import BinanceAccountCreate, BinanceValidationOut
from app.services.audit import write_audit
from app.services.binance.futures_client import BinanceFuturesClient
from app.services.supabase.repositories import BinanceAccountRepository

router = APIRouter(prefix="/binance/accounts", tags=["binance"], dependencies=[Depends(rate_limit_dependency)])


async def validate_credentials(api_key: str, api_secret: str, environment: str) -> BinanceValidationOut:
    client = BinanceFuturesClient(api_key, api_secret, environment)  # type: ignore[arg-type]
    result = await client.validate_futures_access()
    return BinanceValidationOut(
        valid=bool(result["futures_enabled"]),
        futures_enabled=bool(result["futures_enabled"]),
        permissions_detected=result["permissions_detected"],
        message="Binance USD-M Futures access validated." if result["futures_enabled"] else "API key cannot trade USD-M Futures.",
    )


@router.post("")
async def create_account(payload: BinanceAccountCreate, request: Request, user: AuthenticatedUser = Depends(get_current_user)) -> dict:
    validation = await validate_credentials(payload.api_key, payload.api_secret, payload.environment)
    repo = BinanceAccountRepository()
    account = await repo.create(
        {
            "user_id": user.id,
            "label": payload.label,
            "api_key_encrypted": encrypt_secret(payload.api_key),
            "api_secret_encrypted": encrypt_secret(payload.api_secret),
            "api_key_masked": mask_api_key(payload.api_key),
            "environment": payload.environment,
            "permissions_detected": validation.permissions_detected,
            "futures_enabled": validation.futures_enabled,
            "ip_restricted_confirmed": payload.ip_restricted_confirmed,
            "last_validated_at": datetime.now(timezone.utc).isoformat(),
        }
    )
    await write_audit(user.id, "binance_account_connected", "binance_account", account.get("id"), {"environment": payload.environment}, request.client.host if request.client else None, request.headers.get("user-agent"))
    return {"account": {k: v for k, v in account.items() if not k.endswith("_encrypted")}}


@router.get("")
async def list_accounts(user: AuthenticatedUser = Depends(get_current_user)) -> dict:
    accounts = await BinanceAccountRepository().for_user(user.id)
    return {"accounts": [{k: v for k, v in account.items() if not k.endswith("_encrypted")} for account in accounts]}


@router.post("/{account_id}/validate")
async def validate_account(account_id: str, user: AuthenticatedUser = Depends(get_current_user)) -> dict:
    repo = BinanceAccountRepository()
    account = await repo.get_for_user(account_id, user.id)
    if not account:
        raise HTTPException(status_code=404, detail="Binance account not found.")
    validation = await validate_credentials(decrypt_secret(account["api_key_encrypted"]), decrypt_secret(account["api_secret_encrypted"]), account["environment"])
    updated = await repo.update(
        account_id,
        {
            "permissions_detected": validation.permissions_detected,
            "futures_enabled": validation.futures_enabled,
            "last_validated_at": datetime.now(timezone.utc).isoformat(),
        },
    )
    return {"validation": validation, "account": {k: v for k, v in updated.items() if not k.endswith("_encrypted")}}


@router.delete("/{account_id}")
async def delete_account(account_id: str, request: Request, user: AuthenticatedUser = Depends(get_current_user)) -> dict:
    repo = BinanceAccountRepository()
    account = await repo.get_for_user(account_id, user.id)
    if not account:
        raise HTTPException(status_code=404, detail="Binance account not found.")
    await repo.update(account_id, {"deleted_at": datetime.now(timezone.utc).isoformat()})
    await write_audit(user.id, "binance_account_removed", "binance_account", account_id, {}, request.client.host if request.client else None, request.headers.get("user-agent"))
    return {"deleted": True}

