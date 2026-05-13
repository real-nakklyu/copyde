export function money(value: number | string | null | undefined) {
  const num = Number(value ?? 0)
  return new Intl.NumberFormat("en-US", { style: "currency", currency: "USD", maximumFractionDigits: 2 }).format(num)
}

export function percent(value: number | string | null | undefined) {
  return `${Number(value ?? 0).toFixed(2)}%`
}

