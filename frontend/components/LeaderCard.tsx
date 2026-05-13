import Link from "next/link"
import { ShieldCheck } from "lucide-react"
import type { Leader } from "@/types"

export function LeaderCard({ leader }: { leader: Leader }) {
  return (
    <Link href={`/leaders/${leader.id}`} className="block rounded-lg border border-line bg-panel2 p-5 hover:border-binance">
      <div className="flex items-start justify-between gap-4">
        <div>
          <h3 className="text-lg font-semibold text-white">{leader.display_name}</h3>
          <p className="mt-2 line-clamp-2 text-sm text-zinc-400">{leader.description}</p>
        </div>
        <span className="rounded bg-binance/10 px-2 py-1 text-xs text-binance">{leader.source_type}</span>
      </div>
      <div className="mt-5 flex items-center justify-between text-sm">
        <span className="inline-flex items-center gap-2 text-zinc-300">
          <ShieldCheck className="h-4 w-4 text-binance" />
          Risk {leader.risk_score}/100
        </span>
        <span className="text-gain">Leader connected</span>
      </div>
    </Link>
  )
}

