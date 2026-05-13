"use client"

import { useEffect, useState } from "react"
import { BinanceStyleLayout } from "@/components/BinanceStyleLayout"
import { TradeTable } from "@/components/TradeTable"
import { TradingCard } from "@/components/TradingCard"
import { apiFetch } from "@/lib/apiClient"
import type { CopiedTrade } from "@/types"

export default function TradesPage() {
  const [trades, setTrades] = useState<CopiedTrade[]>([])
  useEffect(() => {
    apiFetch<{ trades: CopiedTrade[] }>("/trades").then((r) => setTrades(r.trades)).catch(() => setTrades([]))
  }, [])
  return (
    <BinanceStyleLayout>
      <TradingCard title="Copied Trades">
        <TradeTable trades={trades} />
      </TradingCard>
    </BinanceStyleLayout>
  )
}

