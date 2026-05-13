"use client"

import { useEffect, useState } from "react"
import { BinanceStyleLayout } from "@/components/BinanceStyleLayout"
import { RiskWarningBanner } from "@/components/RiskWarningBanner"
import { TradingCard } from "@/components/TradingCard"
import { apiFetch } from "@/lib/apiClient"
import type { BinanceAccount } from "@/types"

export default function SecurityPage() {
  const [accounts, setAccounts] = useState<BinanceAccount[]>([])
  const refresh = () => apiFetch<{ accounts: BinanceAccount[] }>("/binance/accounts").then((r) => setAccounts(r.accounts))
  useEffect(() => {
    refresh().catch(() => setAccounts([]))
  }, [])
  return (
    <BinanceStyleLayout>
      <div className="space-y-6">
        <RiskWarningBanner />
        <TradingCard title="Connected Binance Accounts">
          <div className="space-y-3">
            {accounts.map((account) => (
              <div key={account.id} className="flex flex-wrap items-center justify-between gap-3 rounded-md border border-line bg-black p-4">
                <div>
                  <div className="font-medium">{account.label}</div>
                  <div className="text-sm text-zinc-400">{account.api_key_masked} · {account.environment}</div>
                </div>
                <button
                  className="rounded-md border border-loss px-3 py-2 text-sm text-loss"
                  onClick={async () => {
                    await apiFetch(`/binance/accounts/${account.id}`, { method: "DELETE" })
                    await refresh()
                  }}
                >
                  Remove key
                </button>
              </div>
            ))}
          </div>
        </TradingCard>
      </div>
    </BinanceStyleLayout>
  )
}

