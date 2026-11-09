import { useEffect, useState } from "react"

const DEFAULT_DELAY_MS = 300

export function useDebouncedValue<T>(value: T, delay = DEFAULT_DELAY_MS): T {
  const [debounced, setDebounced] = useState(value)

  useEffect(() => {
    const timer = window.setTimeout(() => setDebounced(value), delay)
    return () => window.clearTimeout(timer)
  }, [value, delay])

  return debounced
}
