"use client"

import { useState } from "react"
import Link from "next/link"
import { signUp } from "@/lib/auth"

export default function RegisterPage() {
  const [message, setMessage] = useState("")
  return (
    <main className="grid min-h-screen place-items-center bg-ink p-4">
      <form
        aria-label="register form"
        className="w-full max-w-md rounded-lg border border-line bg-panel2 p-8"
        onSubmit={async (event) => {
          event.preventDefault()
          const form = new FormData(event.currentTarget)
          const { error } = await signUp(String(form.get("email")), String(form.get("password")), String(form.get("display_name")))
          setMessage(error ? error.message : "Check your email if confirmations are enabled, then sign in.")
        }}
      >
        <div className="mb-8">
          <div className="mb-3 grid h-10 w-10 place-items-center rounded bg-binance font-black text-black">C</div>
          <h1 className="text-2xl font-semibold">Create your account</h1>
          <p className="mt-2 text-sm text-zinc-400">Connect Binance Futures after registration.</p>
        </div>
        <div className="space-y-4">
          <input name="display_name" required className="w-full rounded-md border border-line bg-black px-3 py-2" placeholder="Display name" />
          <input name="email" type="email" required className="w-full rounded-md border border-line bg-black px-3 py-2" placeholder="Email" />
          <input name="password" type="password" required minLength={8} className="w-full rounded-md border border-line bg-black px-3 py-2" placeholder="Password" />
          <button className="w-full rounded-md bg-binance py-2 font-semibold text-black hover:bg-yellow-400">Register</button>
          {message ? <p className="text-sm text-zinc-300">{message}</p> : null}
        </div>
        <p className="mt-6 text-sm text-zinc-400">
          Already registered? <Link className="text-binance" href="/login">Sign in</Link>
        </p>
      </form>
    </main>
  )
}

