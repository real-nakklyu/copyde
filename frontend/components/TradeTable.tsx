import { money } from "@/lib/formatters"
import type { CopiedTrade } from "@/types"

export function TradeTable({ trades }: { trades: CopiedTrade[] }) {
  return (
    <div className="overflow-x-auto">
      <table className="w-full min-w-[720px] text-left text-sm">
        <thead className="text-xs uppercase text-zinc-500">
          <tr className="border-b border-line">
            <th className="py-3">Symbol</th>
            <th>Side</th>
            <th>Status</th>
            <th>Entry</th>
            <th>Quantity</th>
            <th>PnL</th>
          </tr>
        </thead>
        <tbody>
          {trades.map((trade) => (
            <tr key={trade.id} className="border-b border-line/70">
              <td className="py-3 font-medium">{trade.symbol}</td>
              <td className={trade.side === "LONG" ? "text-gain" : "text-loss"}>{trade.side}</td>
              <td>{trade.status}</td>
              <td>{money(trade.follower_entry_price)}</td>
              <td>{trade.follower_quantity ?? "-"}</td>
              <td>{money(trade.pnl_realized)}</td>
            </tr>
          ))}
          {!trades.length ? (
            <tr>
              <td colSpan={6} className="py-8 text-center text-zinc-500">
                No copied trades yet.
              </td>
            </tr>
          ) : null}
        </tbody>
      </table>
    </div>
  )
}

