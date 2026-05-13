import type { Config } from "tailwindcss"

const config: Config = {
  darkMode: "class",
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}", "./lib/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#050505",
        panel: "#111315",
        panel2: "#181a20",
        line: "#2b3139",
        binance: "#f0b90b",
        gain: "#0ecb81",
        loss: "#f6465d"
      }
    }
  },
  plugins: []
}

export default config

