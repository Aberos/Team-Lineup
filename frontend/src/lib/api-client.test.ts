import { afterEach, beforeEach, describe, expect, it, vi } from "vitest"

import { jsonResponse } from "@/test/render"

import { ApiError, apiRequest } from "./api-client"
import { authStorage } from "./auth-storage"

describe("apiRequest", () => {
  const fetchMock = vi.fn<typeof fetch>()

  beforeEach(() => {
    vi.stubGlobal("fetch", fetchMock)
    localStorage.clear()
  })

  afterEach(() => {
    fetchMock.mockReset()
    vi.unstubAllGlobals()
  })

  it("envia o token como Bearer e serializa o corpo", async () => {
    authStorage.setToken("abc")
    fetchMock.mockResolvedValue(jsonResponse({ id: 1 }))

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
    fetchMock.mockResolvedValue(jsonResponse({ name: ["Obrigatório"] }, 400))

    await expect(apiRequest("/role/")).rejects.toMatchObject({
      status: 400,
      body: { name: ["Obrigatório"] },
    })
  })

  it("limpa o token ao receber 401", async () => {
    authStorage.setToken("expired")
    fetchMock.mockResolvedValue(jsonResponse({ detail: "x" }, 401))

    await expect(apiRequest("/auth/me/")).rejects.toBeInstanceOf(ApiError)
    expect(authStorage.getToken()).toBeNull()
  })

  it("aceita respostas sem corpo", async () => {
    fetchMock.mockResolvedValue(new Response(null, { status: 204 }))

    await expect(apiRequest("/role/1/", { method: "DELETE" })).resolves.toBe(
      null,
    )
  })
})
