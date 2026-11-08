import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { useNavigate } from "react-router"

import { authStorage } from "@/lib/auth-storage"

import { authApi } from "./api"

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
    mutationFn: authApi.login,
    onSuccess: ({ token }) => {
      authStorage.setToken(token)
      queryClient.invalidateQueries({ queryKey: CURRENT_USER_KEY })
    },
  })
}

export function useLogout() {
  const queryClient = useQueryClient()
  const navigate = useNavigate()
  return () => {
    authStorage.clear()
    queryClient.clear()
    navigate("/login", { replace: true })
  }
}
