"use client"

import Link from "next/link"
import { usePathname, useRouter } from "next/navigation"
import { Activity, Bot, CandlestickChart, KeyRound, LayoutDashboard, LogOut, Shield, Users } from "lucide-react"
import { signOut } from "@/lib/auth"
import { cn } from "@/lib/utils"

const nav = [
  { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { href: "/connect-binance", label: "Keys", icon: KeyRound },
  { href: "/leaders", label: "Leaders", icon: Users },
  { href: "/bots/new", label: "New Bot", icon: Bot },
  { href: "/trades", label: "Trades", icon: CandlestickChart },
  { href: "/settings/security", label: "Security", icon: Shield },
  { href: "/admin", label: "Admin", icon: Activity }
]

export function BinanceStyleLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname()
  const router = useRouter()
  return (
    <div className="min-h-screen bg-ink text-zinc-100">
      <aside className="fixed inset-y-0 left-0 hidden w-64 border-r border-line bg-black lg:block">
        <Link href="/dashboard" className="flex h-16 items-center gap-3 border-b border-line px-5">
          <div className="grid h-9 w-9 place-items-center rounded bg-binance text-sm font-black text-black">C</div>
          <div>
            <div className="text-lg font-semibold">Copyde</div>
            <div className="text-xs text-zinc-500">USD-M Futures</div>
          </div>
        </Link>
        <nav className="space-y-1 p-3">
          {nav.map((item) => {
            const Icon = item.icon
            const active = pathname === item.href || pathname.startsWith(`${item.href}/`)
            return (
              <Link
                key={item.href}
                href={item.href}
                className={cn("flex items-center gap-3 rounded-md px-3 py-2 text-sm text-zinc-400 hover:bg-panel hover:text-white", active && "bg-panel text-binance")}
              >
                <Icon className="h-4 w-4" />
                {item.label}
              </Link>
            )
          })}
        </nav>
      </aside>
      <main className="lg:pl-64">
        <header className="sticky top-0 z-20 flex h-16 items-center justify-between border-b border-line bg-black/90 px-4 backdrop-blur lg:px-8">
          <div className="text-sm text-zinc-400">Leader-connected copy trading</div>
          <button
            className="inline-flex items-center gap-2 rounded-md border border-line px-3 py-2 text-sm text-zinc-300 hover:border-binance hover:text-binance"
            onClick={async () => {
              await signOut()
              router.push("/login")
            }}
          >
            <LogOut className="h-4 w-4" />
            Sign out
          </button>
        </header>
        <div className="p-4 lg:p-8">{children}</div>
      </main>
    </div>
  )
}

