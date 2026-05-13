"use client"

import { useEffect, useState } from "react"
import { BinanceStyleLayout } from "@/components/BinanceStyleLayout"
import { LeaderCard } from "@/components/LeaderCard"
import { TradingCard } from "@/components/TradingCard"
import { apiFetch } from "@/lib/apiClient"
import type { Leader } from "@/types"

export default function LeadersPage() {
  const [leaders, setLeaders] = useState<Leader[]>([])
  useEffect(() => {
    apiFetch<{ leaders: Leader[] }>("/leaders").then((r) => setLeaders(r.leaders)).catch(() => setLeaders([]))
  }, [])
  return (
    <BinanceStyleLayout>
      <TradingCard title="Leader Marketplace">
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
          {leaders.map((leader) => <LeaderCard key={leader.id} leader={leader} />)}
          {!leaders.length ? <p className="text-sm text-zinc-500">No active leaders yet. Leader-connected sources appear here after approval.</p> : null}
        </div>
      </TradingCard>
    </BinanceStyleLayout>
  )
}

