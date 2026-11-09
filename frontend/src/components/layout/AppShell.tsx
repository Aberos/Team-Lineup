import { NavLink, Outlet } from "react-router"

import { useCurrentUser } from "@/features/auth/hooks"
import { cn } from "@/lib/utils"

import { UserMenu } from "./UserMenu"

const NAV_ITEMS = [
  { to: "/events", label: "Eventos" },
  { to: "/players", label: "Jogadores" },
  { to: "/roles", label: "Funções" },
  { to: "/attributes", label: "Atributos" },
] as const

const STAFF_NAV_ITEMS = [{ to: "/settings/formula", label: "Fórmula" }] as const

export function AppShell() {
  const user = useCurrentUser()
  const navItems = user.data?.is_staff
    ? [...NAV_ITEMS, ...STAFF_NAV_ITEMS]
    : NAV_ITEMS

  return (
    <div className="min-h-svh bg-background">
      <header className="border-b px-4 py-2">
        <div className="mx-auto flex max-w-6xl flex-wrap items-center gap-x-6 gap-y-1">
          <span className="font-semibold">TeamLineup</span>
          <nav
            aria-label="Principal"
            className="order-last flex w-full gap-4 overflow-x-auto text-sm whitespace-nowrap sm:order-none sm:w-auto"
          >
            {navItems.map((item) => (
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
