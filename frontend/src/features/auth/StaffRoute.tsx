import { Navigate, Outlet } from "react-router"

import { Skeleton } from "@/components/ui/skeleton"

import { useCurrentUser } from "./hooks"

export function StaffRoute() {
  const user = useCurrentUser()

  if (user.isPending) {
    return <Skeleton className="h-40 w-full" />
  }
  if (!user.data?.is_staff) {
    return <Navigate to="/" replace />
  }
  return <Outlet />
}
