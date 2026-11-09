import type { CardAttribute } from "./types"

export type CardTier = {
  label: string
  surface: string
  line: string
  divider: string
  ring: string
}

const ELITE_MIN = 85
const HIGHLIGHT_MIN = 70
const INITIALS_LENGTH = 2

const ELITE: CardTier = {
  label: "Elite",
  surface: "bg-linear-160 from-indigo-950 via-indigo-900 to-indigo-700 text-white",
  line: "border-indigo-200/55",
  divider: "bg-indigo-200/55",
  ring: "border-indigo-200",
}

const HIGHLIGHT: CardTier = {
  label: "Destaque",
  surface: "bg-linear-160 from-teal-950 via-teal-900 to-teal-700 text-white",
  line: "border-teal-200/50",
  divider: "bg-teal-200/50",
  ring: "border-teal-200",
}

const BASE: CardTier = {
  label: "Base",
  surface: "bg-linear-160 from-neutral-950 via-neutral-800 to-neutral-700 text-white",
  line: "border-neutral-200/45",
  divider: "bg-neutral-200/45",
  ring: "border-neutral-300",
}

const UNRATED: CardTier = {
  label: "Sem avaliação",
  surface: "bg-linear-160 from-neutral-100 to-neutral-200 text-neutral-800",
  line: "border-neutral-800/25",
  divider: "bg-neutral-800/25",
  ring: "border-neutral-400",
}

export function tierFor(overall: number | null): CardTier {
  if (overall === null) {
    return UNRATED
  }
  if (overall >= ELITE_MIN) {
    return ELITE
  }
  if (overall >= HIGHLIGHT_MIN) {
    return HIGHLIGHT
  }
  return BASE
}

export function initialsOf(name: string): string {
  return name
    .split(/\s+/)
    .filter(Boolean)
    .slice(0, INITIALS_LENGTH)
    .map((part) => part.charAt(0).toUpperCase())
    .join("")
}

export function splitColumns(
  attributes: ReadonlyArray<CardAttribute>,
): [CardAttribute[], CardAttribute[]] {
  const half = Math.ceil(attributes.length / 2)
  return [attributes.slice(0, half), attributes.slice(half)]
}
