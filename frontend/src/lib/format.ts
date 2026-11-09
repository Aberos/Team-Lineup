const ISO_DATE_PATTERN = /^(\d{4})-(\d{2})-(\d{2})$/

export function formatDate(isoDate: string): string {
  const match = ISO_DATE_PATTERN.exec(isoDate)
  if (match === null) {
    return isoDate
  }
  const [, year, month, day] = match
  return `${day}/${month}/${year}`
}

export function todayIso(): string {
  const now = new Date()
  const month = String(now.getMonth() + 1).padStart(2, "0")
  const day = String(now.getDate()).padStart(2, "0")
  return `${now.getFullYear()}-${month}-${day}`
}

const DATE_TIME_FORMAT = new Intl.DateTimeFormat("pt-BR", {
  dateStyle: "short",
  timeStyle: "short",
})

export function formatDateTime(isoDateTime: string): string {
  const date = new Date(isoDateTime)
  return Number.isNaN(date.getTime()) ? isoDateTime : DATE_TIME_FORMAT.format(date)
}
