from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Request

from app.core.auth import AuthenticatedUser, get_current_user
from app.schemas.leaders import LeaderApply, ManualSignalCreate
from app.services.audit import write_audit
from app.services.supabase.repositories import BinanceAccountRepository, LeaderRepository, TradeSignalRepository

router = APIRouter(prefix="/leaders", tags=["leaders"])


@router.get("")
async def leaders() -> dict:
    return {"leaders": await LeaderRepository().active()}


@router.get("/{leader_id}")
async def leader(leader_id: str) -> dict:
    row = await LeaderRepository().get(leader_id)
    if not row:
        raise HTTPException(status_code=404, detail="Leader not found.")
    return {"leader": row}


@router.post("/apply")
async def apply_as_leader(payload: LeaderApply, request: Request, user: AuthenticatedUser = Depends(get_current_user)) -> dict:
    account = await BinanceAccountRepository().get_for_user(payload.binance_account_id, user.id)
    if not account or not account.get("futures_enabled"):
        raise HTTPException(status_code=400, detail="A validated Binance Futures account is required to become a leader.")
    leader = await LeaderRepository().create(
        {
            "user_id": user.id,
            "display_name": payload.display_name,
            "source_type": "leader_connected",
            "description": payload.description,
            "risk_score": 50,
            "is_active": True,
        }
    )
    await write_audit(user.id, "leader_created", "leader_profile", leader.get("id"), {"source_type": "leader_connected"}, request.client.host if request.client else None, request.headers.get("user-agent"))
    return {"leader": leader}


@router.post("/manual-signal")
async def manual_signal(payload: ManualSignalCreate, user: AuthenticatedUser = Depends(get_current_user)) -> dict:
    leader = await LeaderRepository().get(payload.leader_id)
    if not leader or leader["user_id"] != user.id:
        raise HTTPException(status_code=403, detail="Only the leader can publish manual signals.")
    if leader["source_type"] != "manual_signal":
        raise HTTPException(status_code=400, detail="Manual signals are only enabled for manual_signal leaders.")
    existing = await TradeSignalRepository().by_external(payload.leader_id, payload.external_signal_id)
    if existing:
        return {"signal": existing, "idempotent": True}
    signal = await TradeSignalRepository().create({**payload.model_dump(), "event_time": datetime.now(timezone.utc).isoformat()})
    return {"signal": signal, "idempotent": False}

