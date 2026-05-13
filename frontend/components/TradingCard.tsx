import { cn } from "@/lib/utils"

export function TradingCard({ title, children, className }: { title?: string; children: React.ReactNode; className?: string }) {
  return (
    <section className={cn("rounded-lg border border-line bg-panel2 p-5 shadow-sm", className)}>
      {title ? <h2 className="mb-4 text-sm font-semibold uppercase tracking-wide text-zinc-400">{title}</h2> : null}
      {children}
    </section>
  )
}

