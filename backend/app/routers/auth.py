from __future__ import annotations

from fastapi import APIRouter, Depends

from app.core.auth import AuthenticatedUser, get_current_user
from app.services.supabase.repositories import ProfileRepository

router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/me")
async def me(user: AuthenticatedUser = Depends(get_current_user)) -> dict:
    profile = await ProfileRepository().me(user.id)
    return {"user": {"id": user.id, "email": user.email, "role": user.role}, "profile": profile}

