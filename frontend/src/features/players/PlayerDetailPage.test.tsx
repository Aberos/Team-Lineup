import { screen, waitFor, within } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { afterEach, describe, expect, it, vi } from "vitest"

import { mockApi } from "@/test/mock-api"
import { jsonResponse, noContent, renderWithProviders } from "@/test/render"

import { PlayerDetailPage } from "./PlayerDetailPage"

const PLAYER = {
  id: 1,
  name: "Ana Souza",
  birthday: "1995-04-10",
  phone: "11999990000",
  email: "ana@example.com",
  number: 10,
}
const GOALKEEPER = { id: 5, name: "Goleiro" }
const STRIKER = { id: 6, name: "Atacante" }

const renderDetail = (initialPath = "/players/1") =>
  renderWithProviders(<PlayerDetailPage />, {
    path: "/players/:playerId",
    initialPath,
    extraRoutes: [{ path: "/players", element: <p>Lista de jogadores</p> }],
  })

describe("PlayerDetailPage", () => {
  afterEach(() => {
    vi.unstubAllGlobals()
  })

  it("mostra os dados e as funções do jogador", async () => {
    mockApi({
      "GET /player/1/": PLAYER,
      "GET /player/1/role/": [GOALKEEPER],
      "GET /role/": [GOALKEEPER, STRIKER],
    })

    renderDetail()

    expect(
      await screen.findByRole("heading", { name: "Ana Souza" }),
    ).toBeInTheDocument()
    expect(screen.getByText("10/04/1995")).toBeInTheDocument()
    expect(await screen.findByText("Goleiro")).toBeInTheDocument()
    const select = screen.getByLabelText("Atribuir função")
    expect(within(select).queryByText("Goleiro")).not.toBeInTheDocument()
    expect(within(select).getByText("Atacante")).toBeInTheDocument()
  })

  it("atribui uma função", async () => {
    const api = mockApi({
      "GET /player/1/": PLAYER,
      "GET /player/1/role/": [],
      "GET /role/": [STRIKER],
      "POST /player/1/role/": () => jsonResponse(STRIKER, 201),
    })
    renderDetail()
    await screen.findByText("Nenhuma função atribuída.")

    await userEvent.selectOptions(
      screen.getByLabelText("Atribuir função"),
      "6",
    )
    await userEvent.click(screen.getByRole("button", { name: "Atribuir" }))

    await waitFor(() =>
      expect(api.find("POST", "/player/1/role/")?.body).toEqual({
        role_id: 6,
      }),
    )
  })

  it("exclui o jogador após confirmação", async () => {
    const api = mockApi({
      "GET /player/1/": PLAYER,
      "GET /player/1/role/": [],
      "GET /role/": [],
      "DELETE /player/1/": () => noContent(),
    })
    renderDetail()

    await userEvent.click(await screen.findByRole("button", { name: "Excluir" }))
    const dialog = await screen.findByRole("alertdialog")
    await userEvent.click(within(dialog).getByRole("button", { name: "Excluir" }))

    expect(await screen.findByText("Lista de jogadores")).toBeInTheDocument()
    expect(api.find("DELETE", "/player/1/")).toBeDefined()
  })

  it("mostra jogador não encontrado", async () => {
    mockApi({
      "GET /player/9/": () => jsonResponse({ detail: "Player not found." }, 404),
      "GET /player/9/role/": () => jsonResponse({ detail: "x" }, 404),
      "GET /role/": [],
    })

    renderDetail("/players/9")

    expect(
      await screen.findByText("Jogador não encontrado."),
    ).toBeInTheDocument()
  })
})
