from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Request

from app.core.auth import AuthenticatedUser, get_current_user
from app.schemas.bots import BotCreate, BotUpdateSettings
from app.services.audit import write_audit
from app.services.notifications import notify
from app.services.supabase.repositories import BinanceAccountRepository, BotRepository, LeaderRepository

router = APIRouter(prefix="/bots", tags=["bots"])


@router.post("")
async def create_bot(payload: BotCreate, user: AuthenticatedUser = Depends(get_current_user)) -> dict:
    if not payload.settings.live_trading_acknowledged:
        raise HTTPException(status_code=400, detail="Live trading risk acknowledgement is required before creating a bot.")
    leader = await LeaderRepository().get(payload.leader_id)
    account = await BinanceAccountRepository().get_for_user(payload.binance_account_id, user.id)
    if not leader:
        raise HTTPException(status_code=404, detail="Leader not found.")
    if not account or not account.get("futures_enabled"):
        raise HTTPException(status_code=400, detail="A validated Binance Futures account is required.")
    bot = await BotRepository().create(
        {
            "user_id": user.id,
            "leader_id": payload.leader_id,
            "binance_account_id": payload.binance_account_id,
            "status": "stopped",
            "settings_json": payload.settings.model_dump(mode="json"),
        }
    )
    return {"bot": bot}


@router.get("")
async def list_bots(user: AuthenticatedUser = Depends(get_current_user)) -> dict:
    return {"bots": await BotRepository().for_user(user.id)}


@router.get("/{bot_id}")
async def get_bot(bot_id: str, user: AuthenticatedUser = Depends(get_current_user)) -> dict:
    bot = await BotRepository().get_for_user(bot_id, user.id)
    if not bot:
        raise HTTPException(status_code=404, detail="Bot not found.")
    return {"bot": bot}


@router.post("/{bot_id}/start")
async def start_bot(bot_id: str, request: Request, user: AuthenticatedUser = Depends(get_current_user)) -> dict:
    repo = BotRepository()
    bot = await repo.get_for_user(bot_id, user.id)
    if not bot:
        raise HTTPException(status_code=404, detail="Bot not found.")
    account = await BinanceAccountRepository().get_for_user(bot["binance_account_id"], user.id)
    if not account or not account.get("futures_enabled") or not account.get("last_validated_at"):
        raise HTTPException(status_code=400, detail="Validate the Binance account before starting the bot.")
    if not bot["settings_json"].get("live_trading_acknowledged"):
        raise HTTPException(status_code=400, detail="Live trading risk acknowledgement is required.")
    updated = await repo.update(bot_id, {"status": "running", "started_at": datetime.now(timezone.utc).isoformat(), "error_message": None})
    await write_audit(user.id, "bot_started", "bot", bot_id, {}, request.client.host if request.client else None, request.headers.get("user-agent"))
    await notify(user.id, "Bot started", "Copy trading bot is running.", "success")
    return {"bot": updated}


@router.post("/{bot_id}/pause")
async def pause_bot(bot_id: str, request: Request, user: AuthenticatedUser = Depends(get_current_user)) -> dict:
    bot = await BotRepository().get_for_user(bot_id, user.id)
    if not bot:
        raise HTTPException(status_code=404, detail="Bot not found.")
    updated = await BotRepository().update(bot_id, {"status": "paused"})
    await write_audit(user.id, "bot_paused", "bot", bot_id, {}, request.client.host if request.client else None, request.headers.get("user-agent"))
    await notify(user.id, "Bot paused", "New copied trades are paused.", "warning")
    return {"bot": updated}


@router.post("/{bot_id}/stop")
async def stop_bot(bot_id: str, request: Request, user: AuthenticatedUser = Depends(get_current_user)) -> dict:
    bot = await BotRepository().get_for_user(bot_id, user.id)
    if not bot:
        raise HTTPException(status_code=404, detail="Bot not found.")
    updated = await BotRepository().update(bot_id, {"status": "stopped", "stopped_at": datetime.now(timezone.utc).isoformat()})
    await write_audit(user.id, "bot_stopped", "bot", bot_id, {}, request.client.host if request.client else None, request.headers.get("user-agent"))
    await notify(user.id, "Bot stopped", "Copy trading bot is stopped.", "info")
    return {"bot": updated}


@router.post("/{bot_id}/emergency-close")
async def emergency_close(bot_id: str, request: Request, user: AuthenticatedUser = Depends(get_current_user)) -> dict:
    bot = await BotRepository().get_for_user(bot_id, user.id)
    if not bot:
        raise HTTPException(status_code=404, detail="Bot not found.")
    await BotRepository().update(bot_id, {"status": "stopped", "stopped_at": datetime.now(timezone.utc).isoformat()})
    await write_audit(user.id, "emergency_close_triggered", "bot", bot_id, {"mode": "user_requested"}, request.client.host if request.client else None, request.headers.get("user-agent"))
    await notify(user.id, "Emergency close queued", "Copied positions will be closed by the worker when live trading is enabled.", "error")
    return {"queued": True}


@router.patch("/{bot_id}/settings")
async def update_settings(bot_id: str, payload: BotUpdateSettings, user: AuthenticatedUser = Depends(get_current_user)) -> dict:
    bot = await BotRepository().get_for_user(bot_id, user.id)
    if not bot:
        raise HTTPException(status_code=404, detail="Bot not found.")
    return {"bot": await BotRepository().update(bot_id, {"settings_json": payload.settings.model_dump(mode="json")})}

