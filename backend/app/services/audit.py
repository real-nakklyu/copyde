from __future__ import annotations

from app.services.supabase.repositories import AuditRepository


async def write_audit(
    user_id: str | None,
    action: str,
    entity_type: str,
    entity_id: str | None = None,
    metadata: dict | None = None,
    ip_address: str | None = None,
    user_agent: str | None = None,
) -> None:
    await AuditRepository().create(
        {
            "user_id": user_id,
            "action": action,
            "entity_type": entity_type,
            "entity_id": entity_id,
            "metadata_json": metadata or {},
            "ip_address": ip_address,
            "user_agent": user_agent,
        }
    )

