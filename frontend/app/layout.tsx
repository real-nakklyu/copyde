import type { Metadata } from "next"
import "./globals.css"

export const metadata: Metadata = {
  title: "Copyde | Binance Futures Copy Trading",
  description: "Production-ready leader-connected Binance USD-M Futures copy trading."
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className="dark">
      <body>{children}</body>
    </html>
  )
}

