from __future__ import annotations

import asyncio

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.workers.listenkey_keepalive_tasks import keepalive_all_leader_streams
from app.workers.reconciliation_tasks import reconcile_active_bots
from app.workers.risk_monitor_tasks import monitor_risk


async def main() -> None:
    scheduler = AsyncIOScheduler()
    scheduler.add_job(reconcile_active_bots, "interval", minutes=2)
    scheduler.add_job(keepalive_all_leader_streams, "interval", minutes=50)
    scheduler.add_job(monitor_risk, "interval", seconds=30)
    scheduler.start()
    while True:
        await asyncio.sleep(3600)


if __name__ == "__main__":
    asyncio.run(main())

