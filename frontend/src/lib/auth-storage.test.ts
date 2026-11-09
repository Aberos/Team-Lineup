import { beforeEach, describe, expect, it } from "vitest"

import { authStorage } from "./auth-storage"

describe("authStorage", () => {
  beforeEach(() => {
    localStorage.clear()
    sessionStorage.clear()
  })

  it("guarda a sessão no navegador quando é para manter conectado", () => {
    authStorage.setSession("access", "refresh", true)

    expect(localStorage.getItem("teamlineup.refresh")).toBe("refresh")
    expect(sessionStorage.getItem("teamlineup.refresh")).toBeNull()
    expect(authStorage.getToken()).toBe("access")
  })

  it("guarda a sessão só na aba quando não é para manter conectado", () => {
    authStorage.setSession("access", "refresh", false)

    expect(sessionStorage.getItem("teamlineup.access")).toBe("access")
    expect(localStorage.getItem("teamlineup.access")).toBeNull()
  })

  it("renova os tokens no mesmo lugar da sessão", () => {
    authStorage.setSession("access", "refresh", true)

    authStorage.updateTokens("new-access", "new-refresh")

    expect(localStorage.getItem("teamlineup.access")).toBe("new-access")
    expect(authStorage.getRefreshToken()).toBe("new-refresh")
  })

  it("limpa a sessão mas mantém o usuário lembrado", () => {
    authStorage.setSession("access", "refresh", true)
    authStorage.rememberUsername("ana")

    authStorage.clear()

    expect(authStorage.getToken()).toBeNull()
    expect(authStorage.getRefreshToken()).toBeNull()
    expect(authStorage.getRememberedUsername()).toBe("ana")
    authStorage.forgetUsername()
    expect(authStorage.getRememberedUsername()).toBeNull()
  })
})
