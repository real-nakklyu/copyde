"use client"

import { useEffect, useState } from "react"
import { BinanceStyleLayout } from "@/components/BinanceStyleLayout"
import { PnlChart } from "@/components/PnlChart"
import { RiskWarningBanner } from "@/components/RiskWarningBanner"
import { TradeTable } from "@/components/TradeTable"
import { TradingCard } from "@/components/TradingCard"
import { apiFetch } from "@/lib/apiClient"
import { money } from "@/lib/formatters"

type Summary = {
  total_allocated: string
  open_copied_positions: number
  realized_pnl: string
  unrealized_pnl: string
  active_bots: number
  risk_warnings: Array<Record<string, unknown>>
  recent_copied_trades: []
}

export default function DashboardPage() {
  const [summary, setSummary] = useState<Summary | null>(null)
  useEffect(() => {
    apiFetch<Summary>("/dashboard/summary").then(setSummary).catch(() => setSummary(null))
  }, [])
  const metrics = [
    ["Allocated", money(summary?.total_allocated)],
    ["Open Positions", summary?.open_copied_positions ?? 0],
    ["Realized PnL", money(summary?.realized_pnl)],
    ["Unrealized PnL", money(summary?.unrealized_pnl)],
    ["Active Bots", summary?.active_bots ?? 0]
  ]
  return (
    <BinanceStyleLayout>
      <div className="space-y-6">
        <RiskWarningBanner />
        <div className="grid metric-grid gap-4">
          {metrics.map(([label, value]) => (
            <TradingCard key={label}>
              <div className="text-sm text-zinc-500">{label}</div>
              <div className="mt-2 text-2xl font-semibold">{value}</div>
            </TradingCard>
          ))}
        </div>
        <TradingCard title="PnL">
          <PnlChart />
        </TradingCard>
        <TradingCard title="Recent Copied Trades">
          <TradeTable trades={summary?.recent_copied_trades ?? []} />
        </TradingCard>
      </div>
    </BinanceStyleLayout>
  )
}

