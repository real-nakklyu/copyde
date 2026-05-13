"use client"

import { useEffect, useState } from "react"
import { BinanceStyleLayout } from "@/components/BinanceStyleLayout"
import { RiskWarningBanner } from "@/components/RiskWarningBanner"
import { TradingCard } from "@/components/TradingCard"
import { apiFetch } from "@/lib/apiClient"
import type { BinanceAccount } from "@/types"

export default function ConnectBinancePage() {
  const [accounts, setAccounts] = useState<BinanceAccount[]>([])
  const [message, setMessage] = useState("")
  const refresh = () => apiFetch<{ accounts: BinanceAccount[] }>("/binance/accounts").then((r) => setAccounts(r.accounts)).catch(() => setAccounts([]))
  useEffect(() => {
    refresh()
  }, [])
  return (
    <BinanceStyleLayout>
      <div className="grid gap-6 xl:grid-cols-[1fr_420px]">
        <TradingCard title="Connect Binance Futures">
          <form
            aria-label="connect binance form"
            className="space-y-4"
            onSubmit={async (event) => {
              event.preventDefault()
              const form = new FormData(event.currentTarget)
              await apiFetch("/binance/accounts", {
                method: "POST",
                body: JSON.stringify({
                  label: form.get("label"),
                  api_key: form.get("api_key"),
                  api_secret: form.get("api_secret"),
                  environment: form.get("environment"),
                  ip_restricted_confirmed: form.get("ip_restricted_confirmed") === "on"
                })
              })
              setMessage("Key validated, encrypted, and stored.")
              refresh()
            }}
          >
            <RiskWarningBanner compact />
            <div className="rounded-md border border-line bg-black p-3 text-sm text-zinc-300">
              Create Binance API keys with withdrawal permissions disabled, Futures trading enabled only when needed, and IP whitelisting enabled where possible.
            </div>
            <input name="label" required className="w-full rounded-md border border-line bg-black px-3 py-2" placeholder="Account label" />
            <input name="api_key" required className="w-full rounded-md border border-line bg-black px-3 py-2" placeholder="API key" />
            <input name="api_secret" required type="password" className="w-full rounded-md border border-line bg-black px-3 py-2" placeholder="API secret" />
            <select name="environment" defaultValue="testnet" className="w-full rounded-md border border-line bg-black px-3 py-2">
              <option value="testnet">Binance Futures testnet</option>
              <option value="production">Binance Futures production</option>
            </select>
            <label className="flex items-center gap-3 text-sm text-zinc-300">
              <input name="ip_restricted_confirmed" type="checkbox" className="h-4 w-4 accent-binance" />
              I enabled API IP restrictions where available.
            </label>
            <button className="rounded-md bg-binance px-4 py-2 font-semibold text-black">Validate and save</button>
            {message ? <p className="text-sm text-gain">{message}</p> : null}
          </form>
        </TradingCard>
        <TradingCard title="Connected Keys">
          <div className="space-y-3">
            {accounts.map((account) => (
              <div key={account.id} className="rounded-md border border-line bg-black p-3 text-sm">
                <div className="flex items-center justify-between">
                  <span className="font-medium">{account.label}</span>
                  <span className="text-binance">{account.environment}</span>
                </div>
                <div className="mt-2 text-zinc-400">{account.api_key_masked}</div>
                <div className={account.futures_enabled ? "text-gain" : "text-loss"}>{account.futures_enabled ? "Futures enabled" : "Futures disabled"}</div>
              </div>
            ))}
            {!accounts.length ? <p className="text-sm text-zinc-500">No connected accounts.</p> : null}
          </div>
        </TradingCard>
      </div>
    </BinanceStyleLayout>
  )
}
