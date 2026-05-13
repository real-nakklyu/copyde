"use client"

import { useEffect, useState } from "react"
import { BinanceStyleLayout } from "@/components/BinanceStyleLayout"
import { BotStatusBadge } from "@/components/BotStatusBadge"
import { PositionTable } from "@/components/PositionTable"
import { TradingCard } from "@/components/TradingCard"
import { apiFetch } from "@/lib/apiClient"
import type { Bot } from "@/types"

export default function BotPage({ params }: { params: { id: string } }) {
  const [bot, setBot] = useState<Bot | null>(null)
  const [positions, setPositions] = useState<Array<Record<string, unknown>>>([])
  const refresh = () => apiFetch<{ bot: Bot }>(`/bots/${params.id}`).then((r) => setBot(r.bot))
  useEffect(() => {
    refresh().catch(() => setBot(null))
    apiFetch<{ positions: Array<Record<string, unknown>> }>("/positions/open").then((r) => setPositions(r.positions)).catch(() => setPositions([]))
  }, [params.id])
  async function action(name: "start" | "pause" | "stop" | "emergency-close") {
    await apiFetch(`/bots/${params.id}/${name}`, { method: "POST" })
    await refresh()
  }
  return (
    <BinanceStyleLayout>
      <div className="space-y-6">
        <TradingCard>
          <div className="flex flex-wrap items-center justify-between gap-4">
            <div>
              <h1 className="text-xl font-semibold">Bot {params.id}</h1>
              {bot ? <BotStatusBadge status={bot.status} /> : null}
            </div>
            <div className="flex flex-wrap gap-2">
              <button onClick={() => action("start")} className="rounded-md bg-binance px-3 py-2 text-sm font-semibold text-black">Start</button>
              <button onClick={() => action("pause")} className="rounded-md border border-line px-3 py-2 text-sm">Pause</button>
              <button onClick={() => action("stop")} className="rounded-md border border-line px-3 py-2 text-sm">Stop</button>
              <button onClick={() => action("emergency-close")} className="rounded-md bg-loss px-3 py-2 text-sm font-semibold text-white">Emergency close</button>
            </div>
          </div>
        </TradingCard>
        <TradingCard title="Copied Positions">
          <PositionTable positions={positions} />
        </TradingCard>
        <TradingCard title="Settings">
          <pre className="overflow-auto rounded bg-black p-4 text-xs text-zinc-300">{JSON.stringify(bot?.settings_json ?? {}, null, 2)}</pre>
        </TradingCard>
      </div>
    </BinanceStyleLayout>
  )
}

