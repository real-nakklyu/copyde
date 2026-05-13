from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.core.logging import configure_logging
from app.routers import admin, auth, binance_accounts, bots, dashboard, leaders, trades, users, websocket

configure_logging()
settings = get_settings()

app = FastAPI(title=settings.app_name, version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health() -> dict:
    return {"ok": True, "binance_env": settings.binance_env, "live_trading_disabled": settings.disable_live_trading}


app.include_router(auth.router)
app.include_router(users.router)
app.include_router(binance_accounts.router)
app.include_router(leaders.router)
app.include_router(bots.router)
app.include_router(trades.router)
app.include_router(dashboard.router)
app.include_router(admin.router)
app.include_router(websocket.router)

