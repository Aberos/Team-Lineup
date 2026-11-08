import { NavLink, Outlet } from "react-router"

import { cn } from "@/lib/utils"

import { UserMenu } from "./UserMenu"

const NAV_ITEMS = [
  { to: "/events", label: "Eventos" },
  { to: "/players", label: "Jogadores" },
  { to: "/roles", label: "Funções" },
] as const

export function AppShell() {
  return (
    <div className="min-h-svh bg-background">
      <header className="border-b px-4 py-2">
        <div className="mx-auto flex max-w-6xl flex-wrap items-center gap-x-6 gap-y-1">
          <span className="font-semibold">TeamLineup</span>
          <nav
            aria-label="Principal"
            className="order-last flex w-full gap-4 text-sm sm:order-none sm:w-auto"
          >
            {NAV_ITEMS.map((item) => (
              <NavLink
                key={item.to}
                to={item.to}
                className={({ isActive }) =>
                  cn(
                    "py-1 text-muted-foreground hover:text-foreground",
                    isActive && "font-medium text-foreground",
                  )
                }
              >
                {item.label}
              </NavLink>
            ))}
          </nav>
          <div className="ml-auto">
            <UserMenu />
          </div>
        </div>
      </header>
      <main className="mx-auto max-w-6xl p-4">
        <Outlet />
      </main>
    </div>
  )
}
