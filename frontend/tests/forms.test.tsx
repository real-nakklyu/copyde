import React from "react"
import { render, screen } from "@testing-library/react"
import { describe, expect, it, vi } from "vitest"
import LoginPage from "@/app/login/page"
import RegisterPage from "@/app/register/page"
import ConnectBinancePage from "@/app/connect-binance/page"
import NewBotPage from "@/app/bots/new/page"
import DashboardPage from "@/app/dashboard/page"

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: vi.fn() }),
  usePathname: () => "/dashboard"
}))

vi.mock("@/lib/apiClient", () => ({
  apiFetch: vi.fn(() => Promise.resolve({ accounts: [], leaders: [], trades: [], positions: [] }))
}))

vi.mock("@/lib/auth", () => ({
  signIn: vi.fn(() => Promise.resolve({ error: null })),
  signUp: vi.fn(() => Promise.resolve({ error: null })),
  signOut: vi.fn(() => Promise.resolve({ error: null }))
}))

describe("frontend flows", () => {
  it("renders login and register forms", () => {
    render(React.createElement(LoginPage))
    expect(screen.getByLabelText("login form")).toBeInTheDocument()
    render(React.createElement(RegisterPage))
    expect(screen.getByLabelText("register form")).toBeInTheDocument()
  })

  it("renders connect Binance form validation surface", () => {
    render(React.createElement(ConnectBinancePage))
    expect(screen.getByLabelText("connect binance form")).toBeInTheDocument()
    expect(screen.getByText(/withdrawal permissions/i)).toBeInTheDocument()
  })

  it("renders bot settings and SL TP controls", () => {
    render(React.createElement(NewBotPage, { searchParams: { leader: "leader-1" } }))
    expect(screen.getByLabelText("bot settings form")).toBeInTheDocument()
    expect(screen.getByPlaceholderText("Max daily loss")).toBeInTheDocument()
    expect(screen.getByText(/real Binance Futures orders/i)).toBeInTheDocument()
  })

  it("renders dashboard risk warning", () => {
    render(React.createElement(DashboardPage))
    expect(screen.getByText(/Production trading is disabled by default/i)).toBeInTheDocument()
  })
})
