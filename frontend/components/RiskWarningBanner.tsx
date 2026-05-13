import { AlertTriangle } from "lucide-react"

export function RiskWarningBanner({ compact = false }: { compact?: boolean }) {
  return (
    <div className="flex gap-3 rounded-lg border border-binance/40 bg-binance/10 p-4 text-sm text-zinc-100">
      <AlertTriangle className="mt-0.5 h-5 w-5 shrink-0 text-binance" />
      <p>
        Real Binance Futures trading can liquidate capital. Production trading is disabled by default and requires validated API keys, user acknowledgement,
        admin enablement, and `DISABLE_LIVE_TRADING=false`.
        {compact ? null : " Create API keys without withdrawal permissions and use IP whitelisting wherever Binance allows it."}
      </p>
    </div>
  )
}

