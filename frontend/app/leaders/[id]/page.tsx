"use client"

import { useEffect, useState } from "react"
import Link from "next/link"
import { BinanceStyleLayout } from "@/components/BinanceStyleLayout"
import { PnlChart } from "@/components/PnlChart"
import { TradingCard } from "@/components/TradingCard"
import { apiFetch } from "@/lib/apiClient"
import type { Leader } from "@/types"

export default function LeaderDetailPage({ params }: { params: { id: string } }) {
  const [leader, setLeader] = useState<Leader | null>(null)
  useEffect(() => {
    apiFetch<{ leader: Leader }>(`/leaders/${params.id}`).then((r) => setLeader(r.leader)).catch(() => setLeader(null))
  }, [params.id])
  return (
    <BinanceStyleLayout>
      <div className="space-y-6">
        <TradingCard>
          <div className="flex flex-wrap items-start justify-between gap-4">
            <div>
              <h1 className="text-2xl font-semibold">{leader?.display_name ?? "Leader"}</h1>
              <p className="mt-2 max-w-3xl text-zinc-400">{leader?.description}</p>
            </div>
            <Link href={`/bots/new?leader=${params.id}`} className="rounded-md bg-binance px-4 py-2 font-semibold text-black">Copy leader</Link>
          </div>
        </TradingCard>
        <TradingCard title="Performance">
          <PnlChart />
        </TradingCard>
      </div>
    </BinanceStyleLayout>
  )
}

