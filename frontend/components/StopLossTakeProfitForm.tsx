export function StopLossTakeProfitForm() {
  return (
    <div className="grid gap-4 md:grid-cols-2">
      <label className="space-y-2">
        <span className="text-sm text-zinc-400">Stop loss percent</span>
        <input name="stop_loss_percent" type="number" step="0.1" className="w-full rounded-md border border-line bg-black px-3 py-2" placeholder="2" />
      </label>
      <label className="space-y-2">
        <span className="text-sm text-zinc-400">Take profit percent</span>
        <input name="take_profit_percent" type="number" step="0.1" className="w-full rounded-md border border-line bg-black px-3 py-2" placeholder="4" />
      </label>
      <label className="space-y-2">
        <span className="text-sm text-zinc-400">Fixed SL price</span>
        <input name="stop_loss_price" type="number" step="0.01" className="w-full rounded-md border border-line bg-black px-3 py-2" />
      </label>
      <label className="space-y-2">
        <span className="text-sm text-zinc-400">Fixed TP price</span>
        <input name="take_profit_price" type="number" step="0.01" className="w-full rounded-md border border-line bg-black px-3 py-2" />
      </label>
    </div>
  )
}

