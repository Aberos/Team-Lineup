import { screen } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest"

import { authStorage } from "@/lib/auth-storage"
import { jsonResponse, renderWithProviders } from "@/test/render"

import { LoginPage } from "./LoginPage"

describe("LoginPage", () => {
  const fetchMock = vi.fn<typeof fetch>()

  beforeEach(() => {
    vi.stubGlobal("fetch", fetchMock)
    localStorage.clear()
  })

  afterEach(() => {
    fetchMock.mockReset()
    vi.unstubAllGlobals()
  })

  const renderLogin = () =>
    renderWithProviders(<LoginPage />, {
      path: "/login",
      extraRoutes: [{ path: "/", element: <p>Início</p> }],
    })

  it("valida campos obrigatórios sem chamar a API", async () => {
    renderLogin()

    await userEvent.click(screen.getByRole("button", { name: "Entrar" }))

    expect(await screen.findByText("Informe o usuário")).toBeInTheDocument()
    expect(screen.getByText("Informe a senha")).toBeInTheDocument()
    expect(fetchMock).not.toHaveBeenCalled()
  })

  it("guarda o token e navega após login válido", async () => {
    fetchMock.mockResolvedValue(jsonResponse({ token: "jwt" }))
    renderLogin()

    await userEvent.type(screen.getByLabelText("Usuário"), "ana")
    await userEvent.type(screen.getByLabelText("Senha"), "secret")
    await userEvent.click(screen.getByRole("button", { name: "Entrar" }))

    expect(await screen.findByText("Início")).toBeInTheDocument()
    expect(authStorage.getToken()).toBe("jwt")
  })

  it("mostra o erro devolvido pela API", async () => {
    fetchMock.mockResolvedValue(
      jsonResponse({ detail: "Invalid username or password." }, 400),
    )
    renderLogin()

    await userEvent.type(screen.getByLabelText("Usuário"), "ana")
    await userEvent.type(screen.getByLabelText("Senha"), "errada")
    await userEvent.click(screen.getByRole("button", { name: "Entrar" }))

    expect(
      await screen.findByText("Invalid username or password."),
    ).toBeInTheDocument()
    expect(authStorage.getToken()).toBeNull()
  })
})
