"use client"

import { useEffect, useState } from "react"
import { BinanceStyleLayout } from "@/components/BinanceStyleLayout"
import { TradingCard } from "@/components/TradingCard"
import { apiFetch } from "@/lib/apiClient"

export default function AdminPage() {
  const [status, setStatus] = useState<Record<string, unknown> | null>(null)
  const refresh = () => apiFetch<Record<string, unknown>>("/admin/system-status").then(setStatus).catch(() => setStatus(null))
  useEffect(() => {
    refresh()
  }, [])
  return (
    <BinanceStyleLayout>
      <div className="space-y-6">
        <TradingCard title="Global Trading Controls">
          <pre className="mb-4 overflow-auto rounded bg-black p-4 text-sm text-zinc-300">{JSON.stringify(status, null, 2)}</pre>
          <div className="flex flex-wrap gap-2">
            <button onClick={async () => { await apiFetch("/admin/kill-switch/enable", { method: "POST" }); await refresh() }} className="rounded-md bg-loss px-4 py-2 font-semibold text-white">
              Enable kill switch
            </button>
            <button onClick={async () => { await apiFetch("/admin/kill-switch/disable", { method: "POST" }); await refresh() }} className="rounded-md border border-line px-4 py-2">
              Disable kill switch
            </button>
          </div>
        </TradingCard>
        <TradingCard title="Audit and Error Logs">
          <p className="text-sm text-zinc-400">Use `/admin/audit-logs` and `/admin/error-logs` for full server-side log tables.</p>
        </TradingCard>
      </div>
    </BinanceStyleLayout>
  )
}

