import { screen, waitFor } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { afterEach, describe, expect, it, vi } from "vitest"

import { authStorage } from "@/lib/auth-storage"
import { mockApi } from "@/test/mock-api"
import { renderWithProviders } from "@/test/render"

import { UserMenu } from "./UserMenu"

describe("UserMenu", () => {
  afterEach(() => {
    vi.unstubAllGlobals()
    localStorage.clear()
    sessionStorage.clear()
  })

  it("sai limpando a sessão e invalidando o refresh token", async () => {
    authStorage.setSession("jwt", "refresh-jwt", true)
    authStorage.rememberUsername("ana")
    const api = mockApi({
      "GET /auth/me/": {
        username: "ana",
        first_name: "Ana",
        last_name: "",
        email: "",
        is_staff: false,
      },
      "POST /auth/logout/": {},
    })
    renderWithProviders(<UserMenu />, {
      extraRoutes: [{ path: "/login", element: <p>Tela de login</p> }],
    })

    screen.getByRole("button", { name: "Menu do usuário" }).focus()
    await userEvent.keyboard("{Enter}")
    await userEvent.click(await screen.findByRole("menuitem", { name: "Sair" }))

    expect(await screen.findByText("Tela de login")).toBeInTheDocument()
    expect(authStorage.getToken()).toBeNull()
    expect(authStorage.getRefreshToken()).toBeNull()
    expect(authStorage.getRememberedUsername()).toBe("ana")
    await waitFor(() =>
      expect(api.find("POST", "/auth/logout/")?.body).toEqual({
        refresh: "refresh-jwt",
      }),
    )
  })
})
