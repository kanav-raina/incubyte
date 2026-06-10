export function toNumber(amount: string | null | undefined): number {
  return amount ? Number(amount) : 0
}

/** Formats a number as whole-unit currency, e.g. 94982.79 -> "$94,983". */
export function currencyFormatter(currency: string): (value: number) => string {
  const formatter = new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency,
    maximumFractionDigits: 0,
  })
  return (value: number) => formatter.format(value)
}

/** Compact currency for chart axes, e.g. 120000 -> "$120k". */
export function compactCurrency(value: number): string {
  if (Math.abs(value) >= 1_000_000) return `$${(value / 1_000_000).toFixed(1)}M`
  if (Math.abs(value) >= 1_000) return `$${Math.round(value / 1_000)}k`
  return `$${value}`
}
