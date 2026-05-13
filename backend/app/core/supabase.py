from __future__ import annotations

import httpx
from fastapi import HTTPException

from app.core.config import Settings, get_settings


class SupabaseRestClient:
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()
        if not self.settings.supabase_url or not self.settings.supabase_service_role_key:
            raise HTTPException(status_code=500, detail="Supabase service-role configuration is missing.")
        self.base_url = str(self.settings.supabase_url).rstrip("/")
        self.headers = {
            "apikey": self.settings.supabase_service_role_key,
            "Authorization": f"Bearer {self.settings.supabase_service_role_key}",
            "Content-Type": "application/json",
            "Prefer": "return=representation",
        }

    async def request(self, method: str, table: str, *, params: dict | None = None, json: object | None = None) -> object:
        url = f"{self.base_url}/rest/v1/{table}"
        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.request(method, url, headers=self.headers, params=params, json=json)
        if response.status_code >= 400:
            raise HTTPException(status_code=response.status_code, detail=response.text)
        if not response.content:
            return []
        return response.json()

