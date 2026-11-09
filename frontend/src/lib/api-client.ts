import { withPrefix } from "@/lib/app-prefix"
import { authStorage } from "@/lib/auth-storage"

const API_BASE = withPrefix("/api/v1")
const LOGIN_PATH = withPrefix("/login")
const REFRESH_PATH = "/auth/refresh/"

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

function toRequestBody(body: unknown): BodyInit | undefined {
  if (body === undefined) {
    return undefined
  }
  return body instanceof FormData ? body : JSON.stringify(body)
}

function redirectToLogin(): void {
  authStorage.clear()
  if (window.location.pathname !== LOGIN_PATH) {
    window.location.assign(LOGIN_PATH)
  }
}

type TokenPair = { access: string; refresh: string }

function isTokenPair(value: unknown): value is TokenPair {
  return (
    typeof value === "object" &&
    value !== null &&
    "access" in value &&
    "refresh" in value &&
    typeof value.access === "string" &&
    typeof value.refresh === "string"
  )
}

let pendingRefresh: Promise<string | null> | null = null

async function requestNewTokens(refresh: string): Promise<string | null> {
  try {
    const response = await fetch(`${API_BASE}${REFRESH_PATH}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ refresh }),
    })
    if (!response.ok) {
      return null
    }
    const data: unknown = await response.json()
    if (!isTokenPair(data)) {
      return null
    }
    authStorage.updateTokens(data.access, data.refresh)
    return data.access
  } catch {
    return null
  }
}

function refreshAccessToken(): Promise<string | null> {
  const refresh = authStorage.getRefreshToken()
  if (refresh === null) {
    return Promise.resolve(null)
  }
  if (pendingRefresh === null) {
    pendingRefresh = requestNewTokens(refresh).finally(() => {
      pendingRefresh = null
    })
  }
  return pendingRefresh
}

function send(
  path: string,
  { body, headers, ...init }: RequestOptions,
  token: string | null,
): Promise<Response> {
  const isFormData = body instanceof FormData
  return fetch(`${API_BASE}${path}`, {
    ...init,
    headers: {
      ...(isFormData ? {} : { "Content-Type": "application/json" }),
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...headers,
    },
    body: toRequestBody(body),
  })
}

export async function apiRequest<T>(
  path: string,
  options: RequestOptions = {},
): Promise<T> {
  const token = authStorage.getToken()
  let response = await send(path, options, token)

  if (response.status === 401 && token !== null) {
    const renewed = await refreshAccessToken()
    if (renewed !== null) {
      response = await send(path, options, renewed)
    }
    if (response.status === 401) {
      redirectToLogin()
    }
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
