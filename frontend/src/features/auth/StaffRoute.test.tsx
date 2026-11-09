import { screen } from "@testing-library/react"
import { afterEach, describe, expect, it, vi } from "vitest"

import { AppShell } from "@/components/layout/AppShell"
import { authStorage } from "@/lib/auth-storage"
import { mockApi } from "@/test/mock-api"
import { renderWithProviders } from "@/test/render"

import { StaffRoute } from "./StaffRoute"

const USER = {
  username: "ana",
  first_name: "Ana",
  last_name: "",
  email: "",
}

describe("StaffRoute", () => {
  afterEach(() => {
    vi.unstubAllGlobals()
    localStorage.clear()
    sessionStorage.clear()
  })

  it("redireciona quem não é administrador", async () => {
    authStorage.setSession("jwt", "refresh-jwt", false)
    mockApi({ "GET /auth/me/": { ...USER, is_staff: false } })

    renderWithProviders(<StaffRoute />, {
      path: "/settings",
      extraRoutes: [{ path: "/", element: <p>Início</p> }],
    })

    expect(await screen.findByText("Início")).toBeInTheDocument()
  })

  it("mostra o menu de fórmula só para administradores", async () => {
    authStorage.setSession("jwt", "refresh-jwt", false)
    mockApi({ "GET /auth/me/": { ...USER, is_staff: true } })

    renderWithProviders(<AppShell />)

    expect(
      await screen.findByRole("link", { name: "Fórmula" }),
    ).toHaveAttribute("href", "/settings/formula")
  })

  it("esconde o menu de fórmula de usuários comuns", async () => {
    authStorage.setSession("jwt", "refresh-jwt", false)
    mockApi({ "GET /auth/me/": { ...USER, is_staff: false } })

    renderWithProviders(<AppShell />)

    expect(await screen.findByRole("link", { name: "Jogadores" })).toBeInTheDocument()
    expect(screen.queryByRole("link", { name: "Fórmula" })).not.toBeInTheDocument()
  })
})
