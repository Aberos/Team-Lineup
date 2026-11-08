import { useParams } from "react-router"

const POSITIVE_INTEGER = /^\d+$/

export function useIdParam(name: string): number | null {
  const value = useParams()[name]
  if (value === undefined || !POSITIVE_INTEGER.test(value)) {
    return null
  }
  return Number(value)
}
