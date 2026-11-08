import { withPrefix } from "@/lib/app-prefix"
import { authStorage } from "@/lib/auth-storage"

const API_BASE = withPrefix("/api/v1")
const LOGIN_PATH = withPrefix("/login")

export class ApiError extends Error {
  readonly status: number
  readonly body: unknown

  constructor(status: number, body: unknown) {
    super(`Request failed with status ${status}`)
    this.status = status
    this.body = body
  }
}

type RequestOptions = Omit<RequestInit, "body"> & { body?: unknown }

function redirectToLogin(): void {
  authStorage.clear()
  if (window.location.pathname !== LOGIN_PATH) {
    window.location.assign(LOGIN_PATH)
  }
}

export async function apiRequest<T>(
  path: string,
  { body, headers, ...init }: RequestOptions = {},
): Promise<T> {
  const token = authStorage.getToken()
  const response = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...headers,
    },
    body: body === undefined ? undefined : JSON.stringify(body),
  })

  if (response.status === 401 && token !== null) {
    redirectToLogin()
  }

  const isJson = response.headers
    .get("Content-Type")
    ?.includes("application/json")
  const data: unknown = isJson ? await response.json() : null

  if (!response.ok) {
    throw new ApiError(response.status, data)
  }

  return data as T
}

export function isNotFound(error: unknown): boolean {
  return error instanceof ApiError && error.status === 404
}
