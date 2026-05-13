from datetime import datetime, timedelta, timezone

import jwt

from app.core.auth import verify_supabase_jwt
from app.core.config import Settings


def test_supabase_jwt_verification():
    secret = "test-secret"
    token = jwt.encode(
        {
            "sub": "00000000-0000-0000-0000-000000000001",
            "email": "user@example.com",
            "aud": "authenticated",
            "exp": datetime.now(timezone.utc) + timedelta(minutes=5),
            "app_metadata": {"role": "admin"},
        },
        secret,
        algorithm="HS256",
    )

    user = verify_supabase_jwt(token, Settings(SUPABASE_JWT_SECRET=secret, JWT_AUDIENCE="authenticated"))

    assert user.id.endswith("0001")
    assert user.email == "user@example.com"
    assert user.role == "admin"

