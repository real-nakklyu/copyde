from __future__ import annotations

from dataclasses import dataclass
from typing import Annotated, Any

import jwt
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt import PyJWKClient

from app.core.config import Settings, get_settings


bearer = HTTPBearer(auto_error=False)


@dataclass(slots=True)
class AuthenticatedUser:
    id: str
    email: str | None
    role: str = "follower"
    claims: dict[str, Any] | None = None


def verify_supabase_jwt(token: str, settings: Settings | None = None) -> AuthenticatedUser:
    settings = settings or get_settings()
    options = {"verify_aud": bool(settings.jwt_audience)}
    try:
        if settings.supabase_jwks_url:
            jwk_client = PyJWKClient(str(settings.supabase_jwks_url))
            signing_key = jwk_client.get_signing_key_from_jwt(token)
            claims = jwt.decode(
                token,
                signing_key.key,
                algorithms=["RS256", "ES256"],
                audience=settings.jwt_audience,
                options=options,
            )
        elif settings.supabase_jwt_secret:
            claims = jwt.decode(
                token,
                settings.supabase_jwt_secret,
                algorithms=["HS256"],
                audience=settings.jwt_audience,
                options=options,
            )
        else:
            raise HTTPException(status_code=500, detail="Supabase JWT verification is not configured.")
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired session.") from exc

    subject = claims.get("sub")
    if not subject:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="JWT missing subject.")
    app_meta = claims.get("app_metadata") or {}
    user_meta = claims.get("user_metadata") or {}
    return AuthenticatedUser(
        id=subject,
        email=claims.get("email"),
        role=app_meta.get("role") or user_meta.get("role") or "follower",
        claims=claims,
    )


async def get_current_user(
    request: Request,
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer)],
) -> AuthenticatedUser:
    if not credentials:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing bearer token.")
    user = verify_supabase_jwt(credentials.credentials)
    request.state.user = user
    return user


def require_admin(user: Annotated[AuthenticatedUser, Depends(get_current_user)]) -> AuthenticatedUser:
    settings = get_settings()
    if user.role != "admin" and (user.email or "").lower() not in settings.admins:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required.")
    return user

