import { QueryClientProvider } from "@tanstack/react-query"
import { StrictMode } from "react"
import { createRoot } from "react-dom/client"
import { RouterProvider } from "react-router"

import { Toaster } from "@/components/ui/sonner"
import { queryClient } from "@/lib/query-client"
import { router } from "@/routes"

import "./index.css"

const rootElement = document.getElementById("root")

if (rootElement === null) {
  throw new Error("Root element not found")
}

createRoot(rootElement).render(
  <StrictMode>
    <QueryClientProvider client={queryClient}>
      <RouterProvider router={router} />
      <Toaster richColors />
    </QueryClientProvider>
  </StrictMode>,
)
