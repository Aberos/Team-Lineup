import { screen } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest"

import { authStorage } from "@/lib/auth-storage"
import { mockApi } from "@/test/mock-api"
import { jsonResponse, renderWithProviders } from "@/test/render"

import { LoginPage } from "./LoginPage"

const TOKENS = { token: "jwt", refresh: "refresh-jwt" }

describe("LoginPage", () => {
  beforeEach(() => {
    localStorage.clear()
    sessionStorage.clear()
  })

  afterEach(() => {
    vi.unstubAllGlobals()
  })

  const renderLogin = () =>
    renderWithProviders(<LoginPage />, {
      path: "/login",
      extraRoutes: [{ path: "/", element: <p>Início</p> }],
    })

  const fillAndSubmit = async (username: string, password: string) => {
    await userEvent.clear(screen.getByLabelText("Usuário"))
    await userEvent.type(screen.getByLabelText("Usuário"), username)
    await userEvent.type(screen.getByLabelText("Senha"), password)
    await userEvent.click(screen.getByRole("button", { name: "Entrar" }))
  }

  const storedValues = () =>
    [
      ...Object.values({ ...localStorage }),
      ...Object.values({ ...sessionStorage }),
    ].join(" ")

  it("valida campos obrigatórios sem chamar a API", async () => {
    const api = mockApi({})
    renderLogin()

    await userEvent.click(screen.getByRole("button", { name: "Entrar" }))

    expect(await screen.findByText("Informe o usuário")).toBeInTheDocument()
    expect(screen.getByText("Informe a senha")).toBeInTheDocument()
    expect(api.calls).toHaveLength(0)
  })

  it("guarda a sessão só na aba quando não é para manter conectado", async () => {
    const api = mockApi({ "POST /auth/login/": TOKENS })
    renderLogin()

    await fillAndSubmit("ana", "secret")

    expect(await screen.findByText("Início")).toBeInTheDocument()
    expect(api.find("POST", "/auth/login/")?.body).toEqual({
      username: "ana",
      password: "secret",
    })
    expect(sessionStorage.getItem("teamlineup.refresh")).toBe("refresh-jwt")
    expect(localStorage.getItem("teamlineup.refresh")).toBeNull()
    expect(authStorage.getRememberedUsername()).toBeNull()
    expect(storedValues()).not.toContain("secret")
  })

  it("mantém conectado e lembra o usuário quando marcado", async () => {
    mockApi({ "POST /auth/login/": TOKENS })
    renderLogin()

    await userEvent.click(screen.getByLabelText("Manter conectado"))
    await userEvent.click(screen.getByLabelText("Lembrar meu usuário"))
    await fillAndSubmit("ana", "secret")

    expect(await screen.findByText("Início")).toBeInTheDocument()
    expect(localStorage.getItem("teamlineup.refresh")).toBe("refresh-jwt")
    expect(authStorage.getRememberedUsername()).toBe("ana")
    expect(storedValues()).not.toContain("secret")
  })

  it("preenche o usuário lembrado e permite esquecê-lo", async () => {
    authStorage.rememberUsername("bia")
    mockApi({ "POST /auth/login/": TOKENS })
    renderLogin()

    expect(screen.getByLabelText("Usuário")).toHaveValue("bia")
    expect(screen.getByLabelText("Lembrar meu usuário")).toBeChecked()
    expect(screen.getByLabelText("Manter conectado")).not.toBeChecked()

    await userEvent.click(screen.getByLabelText("Lembrar meu usuário"))
    await userEvent.type(screen.getByLabelText("Senha"), "secret")
    await userEvent.click(screen.getByRole("button", { name: "Entrar" }))

    expect(await screen.findByText("Início")).toBeInTheDocument()
    expect(authStorage.getRememberedUsername()).toBeNull()
  })

  it("mostra o erro devolvido pela API", async () => {
    mockApi({
      "POST /auth/login/": () =>
        jsonResponse({ detail: "Invalid username or password." }, 400),
    })
    renderLogin()

    await fillAndSubmit("ana", "errada")

    expect(
      await screen.findByText("Invalid username or password."),
    ).toBeInTheDocument()
    expect(authStorage.getToken()).toBeNull()
  })
})
