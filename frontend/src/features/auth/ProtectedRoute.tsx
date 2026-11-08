import { Navigate, Outlet } from "react-router"

import { authStorage } from "@/lib/auth-storage"

export function ProtectedRoute() {
  if (authStorage.getToken() === null) {
    return <Navigate to="/login" replace />
  }
  return <Outlet />
}
