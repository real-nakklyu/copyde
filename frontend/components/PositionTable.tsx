export function PositionTable({ positions }: { positions: Array<Record<string, unknown>> }) {
  return (
    <div className="overflow-x-auto">
      <table className="w-full min-w-[640px] text-left text-sm">
        <thead className="text-xs uppercase text-zinc-500">
          <tr className="border-b border-line">
            <th className="py-3">Symbol</th>
            <th>Side</th>
            <th>Qty</th>
            <th>Entry</th>
            <th>Mark</th>
            <th>Unrealized PnL</th>
          </tr>
        </thead>
        <tbody>
          {positions.map((position) => (
            <tr key={String(position.id)} className="border-b border-line/70">
              <td className="py-3 font-medium">{String(position.symbol)}</td>
              <td>{String(position.position_side)}</td>
              <td>{String(position.quantity)}</td>
              <td>{String(position.entry_price ?? "-")}</td>
              <td>{String(position.mark_price ?? "-")}</td>
              <td>{String(position.unrealized_pnl ?? "-")}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

