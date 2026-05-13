from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from app.core.auth import AuthenticatedUser, get_current_user
from app.services.supabase.repositories import CopiedTradeRepository, PositionSnapshotRepository

router = APIRouter(prefix="", tags=["trades"])


@router.get("/trades")
async def trades(user: AuthenticatedUser = Depends(get_current_user)) -> dict:
    return {"trades": await CopiedTradeRepository().for_user(user.id)}


@router.get("/trades/{trade_id}")
async def trade(trade_id: str, user: AuthenticatedUser = Depends(get_current_user)) -> dict:
    row = await CopiedTradeRepository().get(trade_id)
    if not row:
        raise HTTPException(status_code=404, detail="Trade not found.")
    return {"trade": row}


@router.get("/positions/open")
async def open_positions(user: AuthenticatedUser = Depends(get_current_user)) -> dict:
    rows = await PositionSnapshotRepository().list({"user_id": f"eq.{user.id}", "order": "created_at.desc", "limit": "100"})
    return {"positions": rows}

