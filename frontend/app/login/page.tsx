"use client"

import { useState } from "react"
import Link from "next/link"
import { useRouter } from "next/navigation"
import { signIn } from "@/lib/auth"

export default function LoginPage() {
  const router = useRouter()
  const [error, setError] = useState("")
  return (
    <main className="grid min-h-screen place-items-center bg-ink p-4">
      <form
        aria-label="login form"
        className="w-full max-w-md rounded-lg border border-line bg-panel2 p-8"
        onSubmit={async (event) => {
          event.preventDefault()
          setError("")
          const form = new FormData(event.currentTarget)
          const { error: authError } = await signIn(String(form.get("email")), String(form.get("password")))
          if (authError) setError(authError.message)
          else router.push("/dashboard")
        }}
      >
        <div className="mb-8">
          <div className="mb-3 grid h-10 w-10 place-items-center rounded bg-binance font-black text-black">C</div>
          <h1 className="text-2xl font-semibold">Sign in to Copyde</h1>
          <p className="mt-2 text-sm text-zinc-400">Supabase Auth protects the trading dashboard.</p>
        </div>
        <div className="space-y-4">
          <input name="email" type="email" required className="w-full rounded-md border border-line bg-black px-3 py-2" placeholder="Email" />
          <input name="password" type="password" required className="w-full rounded-md border border-line bg-black px-3 py-2" placeholder="Password" />
          <button className="w-full rounded-md bg-binance py-2 font-semibold text-black hover:bg-yellow-400">Sign in</button>
          {error ? <p className="text-sm text-loss">{error}</p> : null}
        </div>
        <p className="mt-6 text-sm text-zinc-400">
          New here? <Link className="text-binance" href="/register">Create an account</Link>
        </p>
      </form>
    </main>
  )
}

