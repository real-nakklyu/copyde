from __future__ import annotations

from app.services.supabase.repositories import LeaderRepository, RiskEventRepository


async def keepalive_all_leader_streams() -> None:
    leaders = await LeaderRepository().list({"source_type": "eq.leader_connected", "is_active": "eq.true"})
    for leader in leaders:
        await RiskEventRepository().create(
            {
                "bot_id": None,
                "event_type": "leader_stream_supervision",
                "severity": "info",
                "message": f"Leader {leader['id']} is eligible for user data stream supervision.",
                "action_taken": "supervised",
            }
        )
