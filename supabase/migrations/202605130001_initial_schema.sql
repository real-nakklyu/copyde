create extension if not exists "pgcrypto";

do $$ begin
  create type user_role as enum ('follower', 'leader', 'admin');
exception when duplicate_object then null; end $$;
do $$ begin
  create type binance_environment as enum ('testnet', 'production');
exception when duplicate_object then null; end $$;
do $$ begin
  create type leader_source_type as enum ('leader_connected', 'official_copy_api', 'manual_signal');
exception when duplicate_object then null; end $$;
do $$ begin
  create type bot_status as enum ('stopped', 'starting', 'running', 'pausing', 'paused', 'stopping', 'error');
exception when duplicate_object then null; end $$;
do $$ begin
  create type signal_side as enum ('LONG', 'SHORT');
exception when duplicate_object then null; end $$;
do $$ begin
  create type signal_action as enum ('OPEN', 'INCREASE', 'PARTIAL_CLOSE', 'CLOSE', 'UPDATE_SL', 'UPDATE_TP');
exception when duplicate_object then null; end $$;
do $$ begin
  create type entry_type as enum ('MARKET', 'LIMIT');
exception when duplicate_object then null; end $$;
do $$ begin
  create type margin_type as enum ('isolated', 'cross');
exception when duplicate_object then null; end $$;
do $$ begin
  create type copied_trade_status as enum ('pending', 'open', 'partially_closed', 'closed', 'failed', 'stopped_by_risk');
exception when duplicate_object then null; end $$;
do $$ begin
  create type risk_severity as enum ('info', 'warning', 'critical');
exception when duplicate_object then null; end $$;
do $$ begin
  create type notification_type as enum ('info', 'warning', 'error', 'success');
exception when duplicate_object then null; end $$;

create or replace function set_updated_at()
returns trigger language plpgsql as $$
begin
  new.updated_at = now();
  return new;
end;
$$;

create table if not exists profiles (
  id uuid primary key references auth.users(id) on delete cascade,
  email text,
  display_name text,
  role user_role not null default 'follower',
  is_active boolean not null default true,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists binance_accounts (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references profiles(id) on delete cascade,
  label text not null,
  api_key_encrypted text not null,
  api_secret_encrypted text not null,
  api_key_masked text not null,
  environment binance_environment not null default 'testnet',
  permissions_detected jsonb not null default '{}'::jsonb,
  futures_enabled boolean not null default false,
  ip_restricted_confirmed boolean not null default false,
  last_validated_at timestamptz,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  deleted_at timestamptz
);

create table if not exists leader_profiles (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references profiles(id) on delete cascade,
  display_name text not null,
  source_type leader_source_type not null default 'leader_connected',
  description text not null default '',
  risk_score integer not null default 50 check (risk_score between 0 and 100),
  is_active boolean not null default true,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists bots (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references profiles(id) on delete cascade,
  leader_id uuid not null references leader_profiles(id),
  binance_account_id uuid not null references binance_accounts(id),
  status bot_status not null default 'stopped',
  settings_json jsonb not null default '{}'::jsonb,
  started_at timestamptz,
  stopped_at timestamptz,
  last_heartbeat_at timestamptz,
  error_message text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists trade_signals (
  id uuid primary key default gen_random_uuid(),
  leader_id uuid not null references leader_profiles(id) on delete cascade,
  external_signal_id text not null,
  symbol text not null,
  side signal_side not null,
  action signal_action not null,
  entry_type entry_type not null default 'MARKET',
  price numeric,
  quantity numeric,
  leverage integer,
  margin_type margin_type not null default 'isolated',
  position_side text,
  raw_payload jsonb not null default '{}'::jsonb,
  event_time timestamptz not null,
  created_at timestamptz not null default now(),
  unique (leader_id, external_signal_id)
);

create table if not exists copied_trades (
  id uuid primary key default gen_random_uuid(),
  bot_id uuid not null references bots(id) on delete cascade,
  trade_signal_id uuid not null references trade_signals(id),
  symbol text not null,
  side signal_side not null,
  status copied_trade_status not null default 'pending',
  follower_entry_price numeric,
  follower_quantity numeric,
  follower_margin numeric,
  leader_reference text,
  stop_loss_price numeric,
  take_profit_price numeric,
  opened_at timestamptz,
  closed_at timestamptz,
  pnl_realized numeric,
  error_message text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists copied_orders (
  id uuid primary key default gen_random_uuid(),
  copied_trade_id uuid not null references copied_trades(id) on delete cascade,
  binance_order_id text,
  client_order_id text not null,
  order_type text not null,
  side text not null,
  position_side text,
  quantity numeric,
  price numeric,
  stop_price numeric,
  reduce_only boolean not null default false,
  close_position boolean not null default false,
  status text not null,
  raw_response jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique (client_order_id)
);

create table if not exists position_snapshots (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references profiles(id) on delete cascade,
  bot_id uuid references bots(id) on delete set null,
  binance_account_id uuid not null references binance_accounts(id),
  symbol text not null,
  position_side text not null,
  quantity numeric not null,
  entry_price numeric,
  mark_price numeric,
  unrealized_pnl numeric,
  leverage integer,
  margin_type text,
  raw_payload jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now()
);

create table if not exists risk_events (
  id uuid primary key default gen_random_uuid(),
  bot_id uuid references bots(id) on delete cascade,
  copied_trade_id uuid references copied_trades(id) on delete set null,
  event_type text not null,
  severity risk_severity not null default 'info',
  message text not null,
  action_taken text,
  created_at timestamptz not null default now()
);

create table if not exists audit_logs (
  id uuid primary key default gen_random_uuid(),
  user_id uuid references profiles(id) on delete set null,
  action text not null,
  entity_type text not null,
  entity_id uuid,
  ip_address text,
  user_agent text,
  metadata_json jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now()
);

create table if not exists notifications (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references profiles(id) on delete cascade,
  title text not null,
  message text not null,
  type notification_type not null default 'info',
  is_read boolean not null default false,
  created_at timestamptz not null default now()
);

create table if not exists api_error_logs (
  id uuid primary key default gen_random_uuid(),
  user_id uuid references profiles(id) on delete set null,
  provider text not null,
  endpoint text not null,
  error_code text,
  message text not null,
  raw_payload jsonb,
  created_at timestamptz not null default now()
);

create table if not exists system_flags (
  key text primary key,
  value jsonb not null,
  updated_at timestamptz not null default now()
);

insert into system_flags (key, value) values ('admin_kill_switch', 'false'::jsonb)
on conflict (key) do nothing;

create index if not exists idx_binance_accounts_user on binance_accounts(user_id) where deleted_at is null;
create index if not exists idx_bots_user_status on bots(user_id, status);
create index if not exists idx_trade_signals_leader_time on trade_signals(leader_id, event_time desc);
create index if not exists idx_copied_trades_bot_status on copied_trades(bot_id, status);
create index if not exists idx_audit_logs_user_time on audit_logs(user_id, created_at desc);

drop trigger if exists profiles_updated_at on profiles;
create trigger profiles_updated_at before update on profiles for each row execute function set_updated_at();
drop trigger if exists binance_accounts_updated_at on binance_accounts;
create trigger binance_accounts_updated_at before update on binance_accounts for each row execute function set_updated_at();
drop trigger if exists leader_profiles_updated_at on leader_profiles;
create trigger leader_profiles_updated_at before update on leader_profiles for each row execute function set_updated_at();
drop trigger if exists bots_updated_at on bots;
create trigger bots_updated_at before update on bots for each row execute function set_updated_at();
drop trigger if exists copied_trades_updated_at on copied_trades;
create trigger copied_trades_updated_at before update on copied_trades for each row execute function set_updated_at();
drop trigger if exists copied_orders_updated_at on copied_orders;
create trigger copied_orders_updated_at before update on copied_orders for each row execute function set_updated_at();

alter table profiles enable row level security;
alter table binance_accounts enable row level security;
alter table leader_profiles enable row level security;
alter table bots enable row level security;
alter table trade_signals enable row level security;
alter table copied_trades enable row level security;
alter table copied_orders enable row level security;
alter table position_snapshots enable row level security;
alter table risk_events enable row level security;
alter table audit_logs enable row level security;
alter table notifications enable row level security;
alter table api_error_logs enable row level security;

create policy "profiles_select_self" on profiles for select using (auth.uid() = id);
create policy "profiles_update_self" on profiles for update using (auth.uid() = id) with check (auth.uid() = id);

create policy "binance_accounts_owner" on binance_accounts for all using (auth.uid() = user_id) with check (auth.uid() = user_id);
create policy "leaders_public_read" on leader_profiles for select using (is_active = true);
create policy "leaders_owner_write" on leader_profiles for all using (auth.uid() = user_id) with check (auth.uid() = user_id);
create policy "bots_owner" on bots for all using (auth.uid() = user_id) with check (auth.uid() = user_id);
create policy "signals_public_read" on trade_signals for select using (true);
create policy "copied_trades_owner_read" on copied_trades for select using (exists (select 1 from bots where bots.id = copied_trades.bot_id and bots.user_id = auth.uid()));
create policy "copied_orders_owner_read" on copied_orders for select using (exists (select 1 from copied_trades ct join bots b on b.id = ct.bot_id where ct.id = copied_orders.copied_trade_id and b.user_id = auth.uid()));
create policy "position_snapshots_owner_read" on position_snapshots for select using (auth.uid() = user_id);
create policy "risk_events_owner_read" on risk_events for select using (exists (select 1 from bots where bots.id = risk_events.bot_id and bots.user_id = auth.uid()));
create policy "audit_logs_owner_read" on audit_logs for select using (auth.uid() = user_id);
create policy "notifications_owner" on notifications for all using (auth.uid() = user_id) with check (auth.uid() = user_id);

create or replace function public.handle_new_user()
returns trigger language plpgsql security definer set search_path = public as $$
begin
  insert into public.profiles (id, email, display_name)
  values (new.id, new.email, coalesce(new.raw_user_meta_data->>'display_name', split_part(new.email, '@', 1)))
  on conflict (id) do nothing;
  return new;
end;
$$;

drop trigger if exists on_auth_user_created on auth.users;
create trigger on_auth_user_created
after insert on auth.users
for each row execute function public.handle_new_user();

