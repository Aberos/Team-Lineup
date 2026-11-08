import { vi } from "vitest"

import { jsonResponse } from "./render"

const API_BASE = "/api/v1"
const NOT_MOCKED_STATUS = 599

export type ApiCall = { method: string; path: string; body: unknown }

type Handler = (call: ApiCall) => Response

export type ApiHandlers = Record<string, Handler | object>

function parseBody(init: RequestInit | undefined): unknown {
  return typeof init?.body === "string" ? JSON.parse(init.body) : undefined
}

export function mockApi(handlers: ApiHandlers) {
  const calls: ApiCall[] = []
  const fetchMock = vi.fn<typeof fetch>(async (input, init) => {
    const call = {
      method: init?.method ?? "GET",
      path: String(input).replace(API_BASE, ""),
      body: parseBody(init),
    }
    calls.push(call)
    const handler = handlers[`${call.method} ${call.path}`]
    if (handler === undefined) {
      return jsonResponse({ detail: "not mocked" }, NOT_MOCKED_STATUS)
    }
    return typeof handler === "function" ? handler(call) : jsonResponse(handler)
  })
  vi.stubGlobal("fetch", fetchMock)
  return {
    calls,
    find: (method: string, path: string) =>
      calls.find((call) => call.method === method && call.path === path),
  }
}
