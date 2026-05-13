import base64
import os

from app.core.config import Settings
from app.core.security import decrypt_secret, encrypt_secret, mask_api_key


def test_encrypt_decrypt_roundtrip_and_masks_key():
    key = base64.urlsafe_b64encode(os.urandom(32)).decode("ascii")
    settings = Settings(ENCRYPTION_MASTER_KEY=key)
    token = encrypt_secret("super-secret", settings)

    assert token != "super-secret"
    assert decrypt_secret(token, settings) == "super-secret"
    assert mask_api_key("abcdef1234567890") == "abcdef****7890"

