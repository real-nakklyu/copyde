import { BotStatus } from "@/types"

const classes: Record<BotStatus, string> = {
  running: "border-gain/40 bg-gain/10 text-gain",
  paused: "border-binance/50 bg-binance/10 text-binance",
  stopped: "border-zinc-600 bg-zinc-800 text-zinc-300",
  starting: "border-binance/50 bg-binance/10 text-binance",
  pausing: "border-binance/50 bg-binance/10 text-binance",
  stopping: "border-zinc-600 bg-zinc-800 text-zinc-300",
  error: "border-loss/50 bg-loss/10 text-loss"
}

export function BotStatusBadge({ status }: { status: BotStatus }) {
  return <span className={`rounded-full border px-2 py-1 text-xs font-medium ${classes[status]}`}>{status}</span>
}

