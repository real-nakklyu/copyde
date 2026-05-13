"use client"

import { Area, AreaChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts"

const data = [
  { day: "Mon", pnl: 120 },
  { day: "Tue", pnl: 80 },
  { day: "Wed", pnl: 190 },
  { day: "Thu", pnl: 160 },
  { day: "Fri", pnl: 260 },
  { day: "Sat", pnl: 210 },
  { day: "Sun", pnl: 310 }
]

export function PnlChart() {
  return (
    <div className="h-64">
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart data={data}>
          <defs>
            <linearGradient id="pnl" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#f0b90b" stopOpacity={0.5} />
              <stop offset="95%" stopColor="#f0b90b" stopOpacity={0} />
            </linearGradient>
          </defs>
          <XAxis dataKey="day" stroke="#71717a" />
          <YAxis stroke="#71717a" />
          <Tooltip contentStyle={{ background: "#181a20", border: "1px solid #2b3139" }} />
          <Area type="monotone" dataKey="pnl" stroke="#f0b90b" fill="url(#pnl)" />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  )
}

