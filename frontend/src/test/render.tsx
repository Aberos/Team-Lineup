import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import { render } from "@testing-library/react"
import type { ReactElement } from "react"
import { createMemoryRouter, RouterProvider } from "react-router"

type RenderOptions = {
  path?: string
  initialPath?: string
  extraRoutes?: Array<{ path: string; element: ReactElement }>
}

export function renderWithProviders(
  element: ReactElement,
  { path = "/", initialPath, extraRoutes = [] }: RenderOptions = {},
) {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false }, mutations: { retry: false } },
  })
  const router = createMemoryRouter([{ path, element }, ...extraRoutes], {
    initialEntries: [initialPath ?? path],
  })
  return render(
    <QueryClientProvider client={queryClient}>
      <RouterProvider router={router} />
    </QueryClientProvider>,
  )
}

export function jsonResponse(body: unknown, status = 200): Response {
  return new Response(JSON.stringify(body), {
    status,
    headers: { "Content-Type": "application/json" },
  })
}

export function noContent(): Response {
  return new Response(null, { status: 204 })
}
