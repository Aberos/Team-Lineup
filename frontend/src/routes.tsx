import { createBrowserRouter, Navigate } from "react-router"

import { AppShell } from "@/components/layout/AppShell"
import { ProtectedRoute } from "@/features/auth/ProtectedRoute"
import { APP_PREFIX } from "@/lib/app-prefix"

export const router = createBrowserRouter(
  [
    {
      path: "/login",
      lazy: async () => ({
        Component: (await import("@/features/auth/LoginPage")).LoginPage,
      }),
    },
    {
      element: <ProtectedRoute />,
      children: [
        {
          element: <AppShell />,
          children: [
            { index: true, element: <Navigate to="/events" replace /> },
            {
              path: "events",
              lazy: async () => ({
                Component: (await import("@/features/events/EventsPage"))
                  .EventsPage,
              }),
            },
            {
              path: "events/:eventId",
              lazy: async () => ({
                Component: (await import("@/features/events/EventDetailPage"))
                  .EventDetailPage,
              }),
            },
            {
              path: "players",
              lazy: async () => ({
                Component: (await import("@/features/players/PlayersPage"))
                  .PlayersPage,
              }),
            },
            {
              path: "players/:playerId",
              lazy: async () => ({
                Component: (
                  await import("@/features/players/PlayerDetailPage")
                ).PlayerDetailPage,
              }),
            },
            {
              path: "roles",
              lazy: async () => ({
                Component: (await import("@/features/players/RolesPage"))
                  .RolesPage,
              }),
            },
          ],
        },
      ],
    },
    { path: "*", element: <Navigate to="/" replace /> },
  ],
  { basename: APP_PREFIX || "/" },
)
