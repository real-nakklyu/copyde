export type Environment = "testnet" | "production"
export type BotStatus = "stopped" | "starting" | "running" | "pausing" | "paused" | "stopping" | "error"

export type BinanceAccount = {
  id: string
  label: string
  api_key_masked: string
  environment: Environment
  futures_enabled: boolean
  ip_restricted_confirmed: boolean
  last_validated_at?: string
}

export type Leader = {
  id: string
  display_name: string
  source_type: "leader_connected" | "official_copy_api" | "manual_signal"
  description: string
  risk_score: number
  is_active: boolean
}

export type Bot = {
  id: string
  leader_id: string
  binance_account_id: string
  status: BotStatus
  settings_json: Record<string, unknown>
}

export type CopiedTrade = {
  id: string
  symbol: string
  side: "LONG" | "SHORT"
  status: string
  follower_entry_price?: string
  follower_quantity?: string
  pnl_realized?: string
}

