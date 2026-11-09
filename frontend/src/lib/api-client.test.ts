import { afterEach, beforeEach, describe, expect, it, vi } from "vitest"

import { mockApi } from "@/test/mock-api"
import { jsonResponse } from "@/test/render"

import { ApiError, apiRequest } from "./api-client"
import { authStorage } from "./auth-storage"

describe("apiRequest", () => {
  beforeEach(() => {
    localStorage.clear()
    sessionStorage.clear()
  })

  afterEach(() => {
    vi.unstubAllGlobals()
  })

  it("envia o token como Bearer e serializa o corpo", async () => {
    authStorage.setSession("abc", "refresh-abc", false)
    const fetchMock = vi.fn<typeof fetch>(async () => jsonResponse({ id: 1 }))
    vi.stubGlobal("fetch", fetchMock)

    const data = await apiRequest<{ id: number }>("/role/", {
      method: "POST",
      body: { name: "Goleiro" },
    })

    expect(data).toEqual({ id: 1 })
    const [url, init] = fetchMock.mock.calls[0]
    expect(url).toBe("/api/v1/role/")
    expect(init?.headers).toMatchObject({ Authorization: "Bearer abc" })
    expect(init?.body).toBe(JSON.stringify({ name: "Goleiro" }))
  })

  it("lança ApiError com o corpo da resposta de erro", async () => {
    mockApi({ "GET /role/": () => jsonResponse({ name: ["Obrigatório"] }, 400) })

    await expect(apiRequest("/role/")).rejects.toMatchObject({
      status: 400,
      body: { name: ["Obrigatório"] },
    })
  })

  it("renova o token expirado e repete a requisição", async () => {
    authStorage.setSession("old-access", "old-refresh", true)
    const api = mockApi({
      "GET /auth/me/": ({ method }) =>
        authStorage.getToken() === "new-access" && method === "GET"
          ? jsonResponse({ username: "ana" })
          : jsonResponse({ detail: "expired" }, 401),
      "POST /auth/refresh/": () =>
        jsonResponse({ access: "new-access", refresh: "new-refresh" }),
    })

    const data = await apiRequest<{ username: string }>("/auth/me/")

    expect(data).toEqual({ username: "ana" })
    expect(api.find("POST", "/auth/refresh/")?.body).toEqual({
      refresh: "old-refresh",
    })
    expect(localStorage.getItem("teamlineup.refresh")).toBe("new-refresh")
  })

  it("faz uma única renovação para requisições simultâneas", async () => {
    authStorage.setSession("old-access", "old-refresh", false)
    const api = mockApi({
      "GET /role/": () =>
        authStorage.getToken() === "new-access"
          ? jsonResponse([])
          : jsonResponse({ detail: "expired" }, 401),
      "POST /auth/refresh/": () =>
        jsonResponse({ access: "new-access", refresh: "new-refresh" }),
    })

    await Promise.all([apiRequest("/role/"), apiRequest("/role/")])

    expect(
      api.calls.filter((call) => call.path === "/auth/refresh/"),
    ).toHaveLength(1)
    expect(sessionStorage.getItem("teamlineup.refresh")).toBe("new-refresh")
  })

  it("limpa a sessão quando a renovação é recusada", async () => {
    authStorage.setSession("old-access", "old-refresh", true)
    mockApi({
      "GET /auth/me/": () => jsonResponse({ detail: "expired" }, 401),
      "POST /auth/refresh/": () => jsonResponse({ detail: "blacklisted" }, 401),
    })

    await expect(apiRequest("/auth/me/")).rejects.toBeInstanceOf(ApiError)
    expect(authStorage.getToken()).toBeNull()
    expect(authStorage.getRefreshToken()).toBeNull()
  })

  it("não tenta renovar sem sessão", async () => {
    const api = mockApi({
      "POST /auth/login/": () => jsonResponse({ detail: "x" }, 401),
    })

    await expect(
      apiRequest("/auth/login/", { method: "POST", body: {} }),
    ).rejects.toBeInstanceOf(ApiError)
    expect(api.find("POST", "/auth/refresh/")).toBeUndefined()
  })

  it("aceita respostas sem corpo", async () => {
    mockApi({
      "DELETE /role/1/": () => new Response(null, { status: 204 }),
    })

    await expect(apiRequest("/role/1/", { method: "DELETE" })).resolves.toBe(
      null,
    )
  })
})
