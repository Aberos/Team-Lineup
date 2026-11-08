import { QueryClient } from "@tanstack/react-query"

const STALE_TIME_MS = 30_000

export const queryClient = new QueryClient({
  defaultOptions: {
    queries: { retry: 1, staleTime: STALE_TIME_MS },
  },
})
