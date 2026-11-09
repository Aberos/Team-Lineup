import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { useNavigate } from "react-router"

import { authStorage } from "@/lib/auth-storage"

import { authApi } from "./api"
import type { LoginValues } from "./schemas"

const CURRENT_USER_KEY = ["auth", "me"] as const

export function useCurrentUser() {
  return useQuery({
    queryKey: CURRENT_USER_KEY,
    queryFn: authApi.me,
    enabled: authStorage.getToken() !== null,
  })
}

export function useLogin() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ username, password }: LoginValues) =>
      authApi.login({ username, password }),
    onSuccess: ({ token, refresh }, values) => {
      authStorage.setSession(token, refresh, values.keepSignedIn)
      if (values.rememberUsername) {
        authStorage.rememberUsername(values.username)
      } else {
        authStorage.forgetUsername()
      }
      return queryClient.invalidateQueries({ queryKey: CURRENT_USER_KEY })
    },
  })
}

export function useLogout() {
  const queryClient = useQueryClient()
  const navigate = useNavigate()
  return () => {
    const refresh = authStorage.getRefreshToken()
    authStorage.clear()
    queryClient.clear()
    navigate("/login", { replace: true })
    if (refresh !== null) {
      authApi.logout(refresh).catch(() => undefined)
    }
  }
}
