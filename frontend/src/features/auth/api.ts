import { apiRequest } from "@/lib/api-client"

import type { CurrentUser, LoginPayload, LoginResponse } from "./types"

export const authApi = {
  login: (payload: LoginPayload) =>
    apiRequest<LoginResponse>("/auth/login/", {
      method: "POST",
      body: payload,
    }),
  me: () => apiRequest<CurrentUser>("/auth/me/"),
}
