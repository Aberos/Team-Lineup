import { describe, expect, it } from "vitest"

import { formatDate } from "./format"

describe("formatDate", () => {
  it("formata datas ISO sem deslocar o fuso", () => {
    expect(formatDate("2026-01-01")).toBe("01/01/2026")
  })

  it("devolve o valor original quando não é uma data ISO", () => {
    expect(formatDate("ontem")).toBe("ontem")
  })
})
