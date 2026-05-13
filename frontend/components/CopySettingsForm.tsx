"use client"

import { useState } from "react"
import { apiFetch } from "@/lib/apiClient"
import { RiskWarningBanner } from "@/components/RiskWarningBanner"
import { StopLossTakeProfitForm } from "@/components/StopLossTakeProfitForm"

export function CopySettingsForm({ leaderId }: { leaderId?: string }) {
  const [message, setMessage] = useState("")
  return (
    <form
      aria-label="bot settings form"
      className="space-y-6"
      onSubmit={async (event) => {
        event.preventDefault()
        const form = new FormData(event.currentTarget)
        const body = {
          leader_id: String(form.get("leader_id") || leaderId),
          binance_account_id: String(form.get("binance_account_id")),
          settings: {
            allocation_mode: form.get("allocation_mode"),
            fixed_margin_usdt: form.get("fixed_margin_usdt") || null,
            balance_percent: form.get("balance_percent") || null,
            proportional_equity_cap_usdt: form.get("proportional_equity_cap_usdt") || null,
            max_margin_per_trade: form.get("max_margin_per_trade"),
            max_total_margin_allocated: form.get("max_total_margin_allocated"),
            max_daily_loss: form.get("max_daily_loss"),
            max_open_copied_positions: Number(form.get("max_open_copied_positions")),
            allowed_symbols: String(form.get("allowed_symbols") || "").split(",").map((s) => s.trim().toUpperCase()).filter(Boolean),
            blocked_symbols: String(form.get("blocked_symbols") || "").split(",").map((s) => s.trim().toUpperCase()).filter(Boolean),
            slippage_tolerance_percent: form.get("slippage_tolerance_percent"),
            leverage_mode: form.get("leverage_mode"),
            custom_leverage: Number(form.get("custom_leverage")),
            max_leverage: Number(form.get("max_leverage")),
            margin_type: form.get("margin_type"),
            stop_loss_percent: form.get("stop_loss_percent") || null,
            stop_loss_price: form.get("stop_loss_price") || null,
            take_profit_percent: form.get("take_profit_percent") || null,
            take_profit_price: form.get("take_profit_price") || null,
            close_behavior: form.get("close_behavior"),
            live_trading_acknowledged: form.get("live_trading_acknowledged") === "on",
            close_if_sltp_fails: form.get("close_if_sltp_fails") === "on"
          }
        }
        await apiFetch("/bots", { method: "POST", body: JSON.stringify(body) })
        setMessage("Bot created. Start it from the bot detail page after reviewing settings.")
      }}
    >
      <RiskWarningBanner compact />
      <div className="grid gap-4 md:grid-cols-2">
        <input name="leader_id" defaultValue={leaderId} className="rounded-md border border-line bg-black px-3 py-2" placeholder="Leader ID" required />
        <input name="binance_account_id" className="rounded-md border border-line bg-black px-3 py-2" placeholder="Binance account ID" required />
        <select name="allocation_mode" className="rounded-md border border-line bg-black px-3 py-2" defaultValue="fixed_margin">
          <option value="fixed_margin">Fixed margin</option>
          <option value="percentage_balance">Percent balance</option>
          <option value="proportional">Proportional</option>
        </select>
        <input name="fixed_margin_usdt" className="rounded-md border border-line bg-black px-3 py-2" placeholder="Fixed margin USDT" defaultValue="50" />
        <input name="balance_percent" className="rounded-md border border-line bg-black px-3 py-2" placeholder="Balance percent" />
        <input name="proportional_equity_cap_usdt" className="rounded-md border border-line bg-black px-3 py-2" placeholder="Proportional cap USDT" />
        <input name="max_margin_per_trade" className="rounded-md border border-line bg-black px-3 py-2" placeholder="Max margin per trade" defaultValue="100" required />
        <input name="max_total_margin_allocated" className="rounded-md border border-line bg-black px-3 py-2" placeholder="Max total allocated" defaultValue="500" required />
        <input name="max_daily_loss" className="rounded-md border border-line bg-black px-3 py-2" placeholder="Max daily loss" defaultValue="100" required />
        <input name="max_open_copied_positions" type="number" className="rounded-md border border-line bg-black px-3 py-2" defaultValue="3" required />
        <input name="allowed_symbols" className="rounded-md border border-line bg-black px-3 py-2" placeholder="Allowed symbols, comma separated" />
        <input name="blocked_symbols" className="rounded-md border border-line bg-black px-3 py-2" placeholder="Blocked symbols, comma separated" />
        <input name="slippage_tolerance_percent" className="rounded-md border border-line bg-black px-3 py-2" defaultValue="0.5" />
        <select name="leverage_mode" className="rounded-md border border-line bg-black px-3 py-2" defaultValue="custom">
          <option value="custom">Custom leverage</option>
          <option value="copy_leader_capped">Copy leader capped</option>
        </select>
        <input name="custom_leverage" type="number" className="rounded-md border border-line bg-black px-3 py-2" defaultValue="5" />
        <input name="max_leverage" type="number" className="rounded-md border border-line bg-black px-3 py-2" defaultValue="20" />
        <select name="margin_type" className="rounded-md border border-line bg-black px-3 py-2" defaultValue="isolated">
          <option value="isolated">Isolated</option>
          <option value="cross">Cross</option>
        </select>
        <select name="close_behavior" className="rounded-md border border-line bg-black px-3 py-2" defaultValue="leader_or_sl_tp">
          <option value="leader_close">Close when leader closes</option>
          <option value="sl_tp_only">Close only on SL/TP</option>
          <option value="leader_or_sl_tp">Leader close or SL/TP</option>
        </select>
      </div>
      <StopLossTakeProfitForm />
      <label className="flex items-center gap-3 text-sm text-zinc-300">
        <input name="close_if_sltp_fails" type="checkbox" defaultChecked className="h-4 w-4 accent-binance" />
        Close position if protective SL/TP placement fails
      </label>
      <label className="flex items-start gap-3 text-sm text-zinc-300">
        <input name="live_trading_acknowledged" type="checkbox" className="mt-1 h-4 w-4 accent-binance" required />
        I understand this bot can place real Binance Futures orders and lose money.
      </label>
      <button className="rounded-md bg-binance px-4 py-2 font-semibold text-black hover:bg-yellow-400">Create bot</button>
      {message ? <p className="text-sm text-gain">{message}</p> : null}
    </form>
  )
}

