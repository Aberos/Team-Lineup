const TOKEN_KEY = "teamlineup.token"

export const authStorage = {
  getToken(): string | null {
    return localStorage.getItem(TOKEN_KEY)
  },
  setToken(token: string): void {
    localStorage.setItem(TOKEN_KEY, token)
  },
  clear(): void {
    localStorage.removeItem(TOKEN_KEY)
  },
}
