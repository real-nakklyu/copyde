from __future__ import annotations

import os

from fastapi import APIRouter, Depends

from app.core.auth import AuthenticatedUser, require_admin
from app.core.config import get_settings
from app.services.supabase.repositories import ApiErrorLogRepository, AuditRepository

router = APIRouter(prefix="/admin", tags=["admin"])

KILL_SWITCH_ENV = "COPYDE_ADMIN_KILL_SWITCH"


@router.get("/system-status")
async def system_status(_: AuthenticatedUser = Depends(require_admin)) -> dict:
    settings = get_settings()
    return {
        "disable_live_trading": settings.disable_live_trading,
        "enable_production_trading": settings.enable_production_trading,
        "binance_env": settings.binance_env,
        "admin_kill_switch": os.getenv(KILL_SWITCH_ENV, "false").lower() == "true",
    }


@router.post("/kill-switch/enable")
async def enable_kill_switch(_: AuthenticatedUser = Depends(require_admin)) -> dict:
    os.environ[KILL_SWITCH_ENV] = "true"
    return {"admin_kill_switch": True}


@router.post("/kill-switch/disable")
async def disable_kill_switch(_: AuthenticatedUser = Depends(require_admin)) -> dict:
    os.environ[KILL_SWITCH_ENV] = "false"
    return {"admin_kill_switch": False}


@router.get("/audit-logs")
async def audit_logs(_: AuthenticatedUser = Depends(require_admin)) -> dict:
    return {"logs": await AuditRepository().list({"order": "created_at.desc", "limit": "200"})}


@router.get("/error-logs")
async def error_logs(_: AuthenticatedUser = Depends(require_admin)) -> dict:
    return {"logs": await ApiErrorLogRepository().list({"order": "created_at.desc", "limit": "200"})}

