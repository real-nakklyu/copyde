from __future__ import annotations

from app.services.supabase.repositories import NotificationRepository


async def notify(user_id: str, title: str, message: str, type_: str = "info") -> None:
    await NotificationRepository().create({"user_id": user_id, "title": title, "message": message, "type": type_, "is_read": False})

