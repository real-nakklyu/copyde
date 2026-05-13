# Copyde

Production-oriented real-money Binance USD-M Futures copy-trading monorepo.

Copyde uses leader-connected mode first: a leader links their own Binance Futures API account, the backend monitors leader account/order events, normalizes those events into trade signals, and follower bots copy eligible signals into each follower's connected Binance Futures account according to risk settings.

This is not a scraper-based product. Public Binance leader scraping is not implemented. Official Binance Copy Trading endpoints are represented by an abstraction only and must not be treated as supported until Binance exposes the needed API surface for your account and jurisdiction.

## Stack

- Frontend: Next.js 16, TypeScript, Tailwind CSS, Recharts, Supabase Auth.
- Backend: Python FastAPI, AES-GCM credential encryption, Binance USD-M Futures REST/User Data Stream clients.
- Workers: Python APScheduler service for long-running bot, listenKey, reconciliation, and risk supervision.
- Database/Auth/Realtime: Supabase PostgreSQL/Auth/RLS.
- Deployment: frontend on Vercel; backend and worker on Railway, Render, Fly.io, or another Python host.

## Important Safety Defaults

Live trading is blocked by default.

For any production Binance order, all of these must be true:

- The user accepted live trading risk in bot settings.
- The Binance key has been validated for USD-M Futures access.
- The bot status is `running`.
- `DISABLE_LIVE_TRADING=false`.
- `ENABLE_PRODUCTION_TRADING=true` when the account environment is `production`.
- Admin kill switch is not active.
- Risk guard allows the symbol, sizing, daily loss, open position count, and allocation.

Never create Binance keys with withdrawal permission. Copyde has no withdrawal code path.

## Repository Layout

- `frontend/`: Next.js app for Vercel.
- `backend/`: FastAPI app and worker code.
- `supabase/migrations/`: SQL schema, RLS, triggers, enums, indexes.
- `.env.example`: required environment variables.

## Local Setup

1. Create a Supabase project.
2. Apply SQL from `supabase/migrations/202605130001_initial_schema.sql`.
3. Copy `.env.example` to local env files for frontend/backend.
4. Generate an AES key:

```powershell
python -c "import base64, os; print(base64.urlsafe_b64encode(os.urandom(32)).decode())"
```

5. Backend:

```powershell
cd backend
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --reload --port 8000
```

6. Worker in a separate terminal:

```powershell
cd backend
python -m app.workers.worker
```

7. Frontend:

```powershell
cd frontend
npm install
npm run dev
```

Open `http://localhost:3000`.

## Environment Variables

Frontend:

- `NEXT_PUBLIC_SUPABASE_URL`
- `NEXT_PUBLIC_SUPABASE_ANON_KEY`
- `NEXT_PUBLIC_API_URL`

Backend:

- `SUPABASE_URL`
- `SUPABASE_SERVICE_ROLE_KEY`
- `SUPABASE_JWT_SECRET` or `SUPABASE_JWKS_URL`
- `DATABASE_URL`
- `REDIS_URL`
- `ENCRYPTION_MASTER_KEY`
- `JWT_AUDIENCE=authenticated`
- `BINANCE_ENV=testnet|production`
- `DISABLE_LIVE_TRADING=true`
- `ENABLE_PRODUCTION_TRADING=false`
- `ALLOWED_ORIGINS`
- `ADMIN_EMAILS`

Do not expose `SUPABASE_SERVICE_ROLE_KEY` or `ENCRYPTION_MASTER_KEY` to the frontend.

## Supabase Setup

Use Supabase Auth for signup/login. The migration creates `profiles` rows from `auth.users`, enables RLS, and lets users read/write their own records while backend service-role operations can perform trusted trading writes.

Backend requests verify Supabase JWTs before protected actions. If your Supabase project uses asymmetric JWT signing, configure `SUPABASE_JWKS_URL`; otherwise configure `SUPABASE_JWT_SECRET`.

## Binance Setup

Use Binance USD-M Futures.

Official docs used for this implementation:

- [USD-M Futures General Info](https://developers.binance.com/docs/derivatives/usds-margined-futures/general-info)
- [New Order endpoint](https://developers.binance.com/docs/derivatives/usds-margined-futures/trade/rest-api/New-Order)
- [Exchange Information](https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Exchange-Information)
- [Start User Data Stream](https://developers.binance.com/docs/derivatives/usds-margined-futures/user-data-streams/Start-User-Data-Stream)
- [Keepalive User Data Stream](https://developers.binance.com/docs/derivatives/usds-margined-futures/user-data-streams/Keepalive-User-Data-Stream)

Base URLs:

- Production REST: `https://fapi.binance.com`
- Testnet REST: `https://demo-fapi.binance.com`

Create API keys with:

- Withdrawal disabled.
- Futures trading enabled only if the account will trade.
- IP whitelist enabled where possible.
- Separate keys for testnet and production.

## Leader-Connected Mode

1. Leader registers.
2. Leader connects and validates Binance Futures API credentials.
3. Leader applies as a leader source.
4. Worker monitors leader User Data Stream and normalizes order events.
5. `process_leader_signal` stores each signal idempotently by `leader_id + external_signal_id`.
6. Running follower bots copy new signals through their own Binance accounts.

The copy executor starts with MARKET order copy mode and places protective `STOP_MARKET` / `TAKE_PROFIT_MARKET` orders where configured.

## Follower Copy Settings

Supported settings include:

- Allocation: fixed margin, percentage of available USDT balance, proportional exposure.
- Risk: max margin per trade, max total allocation, max daily loss, max open copied positions.
- Symbols: allowlist and blocklist.
- Leverage: custom leverage or copy leader leverage capped by follower max.
- Margin: isolated or cross.
- SL/TP: percent or fixed price, with close-if-protective-order-fails.
- Close behavior: leader close, SL/TP only, or whichever happens first.

## Deployment

Frontend on Vercel:

1. Set Vercel root directory to `frontend`.
2. Add frontend env vars.
3. Deploy with the included `frontend/vercel.json`.

Backend on Railway/Render/Fly:

1. Set root to `backend`.
2. Use `backend/Dockerfile` or run `uvicorn app.main:app --host 0.0.0.0 --port $PORT`.
3. Add backend env vars.
4. Restrict `ALLOWED_ORIGINS` to the Vercel domain.

Worker deployment:

Run a separate long-running Python process:

```bash
python -m app.workers.worker
```

Do not deploy long-running trading workers to Vercel serverless functions.

## Enabling Production Trading

1. Test end to end on Binance Futures testnet first.
2. Set backend `BINANCE_ENV=production`.
3. Set `DISABLE_LIVE_TRADING=false`.
4. Set `ENABLE_PRODUCTION_TRADING=true`.
5. Confirm admin kill switch is disabled.
6. Validate each production Binance account before starting bots.

## Tests

Backend:

```powershell
cd backend
python -m pytest app/tests -q
```

Frontend:

```powershell
cd frontend
npm test
npm run build
npm audit --audit-level=moderate
```

Current local verification:

- Backend tests: 12 passed.
- Frontend tests: 4 passed.
- Frontend production build: passed.
- npm audit: 0 vulnerabilities.

## Known Limitations

- Official Binance Copy Trading API support is not enabled; the abstraction is intentionally non-claiming.
- Manual signal-provider mode is scaffolded for approved manual leaders only.
- User Data Stream runners must be supervised carefully in production, with reconnection and alerting.
- Reconciliation reports alert on mismatches and do not blindly close orphaned positions unless you explicitly add an auto-fix policy.
- This software can place real leveraged derivatives orders. Operate it only after legal, compliance, security, and exchange-policy review.
