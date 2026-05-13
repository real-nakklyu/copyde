from __future__ import annotations

from fastapi import APIRouter, Depends

from app.core.auth import AuthenticatedUser, get_current_user
from app.services.supabase.repositories import ProfileRepository

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me")
async def current_profile(user: AuthenticatedUser = Depends(get_current_user)) -> dict:
    return {"profile": await ProfileRepository().me(user.id)}

