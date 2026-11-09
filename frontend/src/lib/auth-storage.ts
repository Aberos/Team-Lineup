const ACCESS_KEY = "teamlineup.access"
const REFRESH_KEY = "teamlineup.refresh"
const USERNAME_KEY = "teamlineup.username"
const LEGACY_TOKEN_KEY = "teamlineup.token"

function readSession(key: string): string | null {
  return localStorage.getItem(key) ?? sessionStorage.getItem(key)
}

function sessionStore(): Storage {
  return localStorage.getItem(REFRESH_KEY) !== null ? localStorage : sessionStorage
}

function clearSession(): void {
  for (const storage of [localStorage, sessionStorage]) {
    storage.removeItem(ACCESS_KEY)
    storage.removeItem(REFRESH_KEY)
    storage.removeItem(LEGACY_TOKEN_KEY)
  }
}

export const authStorage = {
  getToken(): string | null {
    return readSession(ACCESS_KEY)
  },
  getRefreshToken(): string | null {
    return readSession(REFRESH_KEY)
  },
  setSession(access: string, refresh: string, persistent: boolean): void {
    clearSession()
    const storage = persistent ? localStorage : sessionStorage
    storage.setItem(ACCESS_KEY, access)
    storage.setItem(REFRESH_KEY, refresh)
  },
  updateTokens(access: string, refresh: string): void {
    const storage = sessionStore()
    storage.setItem(ACCESS_KEY, access)
    storage.setItem(REFRESH_KEY, refresh)
  },
  clear(): void {
    clearSession()
  },
  getRememberedUsername(): string | null {
    return localStorage.getItem(USERNAME_KEY)
  },
  rememberUsername(username: string): void {
    localStorage.setItem(USERNAME_KEY, username)
  },
  forgetUsername(): void {
    localStorage.removeItem(USERNAME_KEY)
  },
}
