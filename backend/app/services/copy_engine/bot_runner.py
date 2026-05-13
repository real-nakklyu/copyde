from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal

from app.core.security import decrypt_secret
from app.schemas.bots import BotSettings
from app.services.audit import write_audit
from app.services.binance.exchange_info import SymbolRules
from app.services.binance.futures_client import BinanceFuturesClient
from app.services.copy_engine.copy_executor import execute_open_signal
from app.services.copy_engine.risk_guard import RiskContext, evaluate_risk
from app.services.notifications import notify
from app.services.supabase.repositories import (
    ApiErrorLogRepository,
    BinanceAccountRepository,
    BotRepository,
    CopiedOrderRepository,
    CopiedTradeRepository,
    TradeSignalRepository,
)


def _find_rules(exchange_info: dict, symbol: str) -> SymbolRules:
    for item in exchange_info.get("symbols", []):
        if item.get("symbol") == symbol:
            return SymbolRules.from_exchange_symbol(item)
    raise ValueError(f"Symbol {symbol} is not present in Binance exchangeInfo.")


def _available_usdt(balance_payload: list[dict]) -> Decimal:
    for asset in balance_payload:
        if asset.get("asset") == "USDT":
            return Decimal(str(asset.get("availableBalance") or asset.get("balance") or "0"))
    return Decimal("0")


async def process_leader_signal(signal_payload: dict) -> dict:
    signal_repo = TradeSignalRepository()
    existing = await signal_repo.by_external(signal_payload["leader_id"], signal_payload["external_signal_id"])
    signal = existing or await signal_repo.create(
        {
            **signal_payload,
            "event_time": signal_payload.get("event_time") or datetime.now(timezone.utc).isoformat(),
            "raw_payload": signal_payload.get("raw_payload") or {},
        }
    )
    if existing:
        return {"signal": signal, "idempotent": True, "copied": 0, "failed": 0}

    copied = 0
    failed = 0
    bots = await BotRepository().running_for_leader(signal_payload["leader_id"])
    for bot in bots:
        copied_trade = await CopiedTradeRepository().create(
            {
                "bot_id": bot["id"],
                "trade_signal_id": signal["id"],
                "symbol": signal_payload["symbol"],
                "side": signal_payload["side"],
                "status": "pending",
                "leader_reference": signal_payload["external_signal_id"],
            }
        )
        try:
            account = await BinanceAccountRepository().get_for_user(bot["binance_account_id"], bot["user_id"])
            if not account:
                raise ValueError("Follower Binance account is missing.")
            client = BinanceFuturesClient(decrypt_secret(account["api_key_encrypted"]), decrypt_secret(account["api_secret_encrypted"]), account["environment"])
            bot_settings = BotSettings.model_validate(bot["settings_json"])
            symbol = signal_payload["symbol"].upper()
            exchange_info = await client.exchange_info()
            rules = _find_rules(exchange_info, symbol)
            balance = _available_usdt(await client.balance())
            mark_price = Decimal(str((await client.mark_price(symbol))["markPrice"]))
            risk = evaluate_risk(
                bot_settings,
                RiskContext(
                    bot_status=bot["status"],
                    account_environment=account["environment"],
                    symbol=symbol,
                    daily_loss=Decimal("0"),
                    open_positions=0,
                    total_allocated_margin=Decimal("0"),
                    quantity=Decimal("1"),
                    futures_enabled=bool(account["futures_enabled"]),
                    account_validated=bool(account["last_validated_at"]),
                    user_acknowledged_live_risk=bool(bot_settings.live_trading_acknowledged),
                ),
            )
            if not risk.allowed:
                await CopiedTradeRepository().update(copied_trade["id"], {"status": "stopped_by_risk", "error_message": "; ".join(risk.reasons)})
                await notify(bot["user_id"], "Trade blocked by risk guard", "; ".join(risk.reasons), "warning")
                continue
            mode = await client.position_mode()
            result = await execute_open_signal(
                client=client,
                bot_id=bot["id"],
                copied_trade_id=copied_trade["id"],
                signal={**signal_payload, "symbol": symbol, "price": signal_payload.get("price") or mark_price},
                bot_settings=bot_settings,
                rules=rules,
                available_balance=balance,
                hedge_mode=bool(mode.get("dualSidePosition")),
            )
            entry = result["entry_order"]
            await CopiedOrderRepository().create(
                {
                    "copied_trade_id": copied_trade["id"],
                    "binance_order_id": str(entry.get("orderId")),
                    "client_order_id": entry.get("clientOrderId"),
                    "order_type": entry.get("type", "MARKET"),
                    "side": entry.get("side"),
                    "position_side": entry.get("positionSide"),
                    "quantity": entry.get("origQty") or result["quantity"],
                    "price": entry.get("avgPrice") or result["entry_price"],
                    "status": entry.get("status", "NEW"),
                    "raw_response": entry,
                }
            )
            for protective in result["protective_orders"]:
                await CopiedOrderRepository().create(
                    {
                        "copied_trade_id": copied_trade["id"],
                        "binance_order_id": str(protective.get("orderId")),
                        "client_order_id": protective.get("clientOrderId"),
                        "order_type": protective.get("type"),
                        "side": protective.get("side"),
                        "position_side": protective.get("positionSide"),
                        "quantity": protective.get("origQty"),
                        "stop_price": protective.get("stopPrice"),
                        "close_position": bool(protective.get("closePosition")),
                        "status": protective.get("status", "NEW"),
                        "raw_response": protective,
                    }
                )
            await CopiedTradeRepository().update(
                copied_trade["id"],
                {
                    "status": "open",
                    "follower_entry_price": result["entry_price"],
                    "follower_quantity": result["quantity"],
                    "opened_at": datetime.now(timezone.utc).isoformat(),
                },
            )
            await write_audit(bot["user_id"], "trade_copied", "copied_trade", copied_trade["id"], {"symbol": symbol})
            await notify(bot["user_id"], "Trade copied", f"Copied {symbol} {signal_payload['side']} from leader.", "success")
            copied += 1
        except Exception as exc:
            failed += 1
            await CopiedTradeRepository().update(copied_trade["id"], {"status": "failed", "error_message": str(exc)})
            await ApiErrorLogRepository().create(
                {
                    "user_id": bot["user_id"],
                    "provider": "binance",
                    "endpoint": "copy_engine.process_leader_signal",
                    "error_code": exc.__class__.__name__,
                    "message": str(exc),
                    "raw_payload": {"signal_id": signal.get("id"), "bot_id": bot["id"]},
                }
            )
            await write_audit(bot["user_id"], "order_failed", "copied_trade", copied_trade["id"], {"error": str(exc)})
            await notify(bot["user_id"], "Order failed", str(exc), "error")
    return {"signal": signal, "idempotent": False, "copied": copied, "failed": failed}
