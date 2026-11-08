import { describe, expect, it, vi } from "vitest"

import { ApiError } from "./api-client"
import { applyApiErrors } from "./form-errors"

type Values = { name: string }

describe("applyApiErrors", () => {
  it("mapeia erros de campo do DRF", () => {
    const setError = vi.fn()

    applyApiErrors<Values>(
      new ApiError(400, { name: ["Muito longo"] }),
      ["name"],
      setError,
    )

    expect(setError).toHaveBeenCalledWith("name", { message: "Muito longo" })
    expect(setError).toHaveBeenCalledTimes(1)
  })

  it("usa detail como erro geral do formulário", () => {
    const setError = vi.fn()

    applyApiErrors<Values>(
      new ApiError(409, { detail: "Conflito" }),
      ["name"],
      setError,
    )

    expect(setError).toHaveBeenCalledWith("root", { message: "Conflito" })
  })

  it("usa mensagem padrão para erros desconhecidos", () => {
    const setError = vi.fn()

    applyApiErrors<Values>(new Error("falha"), ["name"], setError)

    expect(setError).toHaveBeenCalledWith("root", {
      message: "Não foi possível concluir a operação.",
    })
  })
})
