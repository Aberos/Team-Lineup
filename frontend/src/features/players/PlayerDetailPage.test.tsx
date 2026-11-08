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
const PASS = { id: 30, name: "Passe" }
const SPEED = { id: 31, name: "Velocidade" }
const NO_ATTRIBUTES = {
  "GET /player/1/attribute/": [],
  "GET /attribute/": [],
}

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
      ...NO_ATTRIBUTES,
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
      ...NO_ATTRIBUTES,
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
      ...NO_ATTRIBUTES,
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

describe("PlayerDetailPage atributos", () => {
  afterEach(() => {
    vi.unstubAllGlobals()
  })

  const baseHandlers = {
    "GET /player/1/": PLAYER,
    "GET /player/1/role/": [],
    "GET /role/": [],
  }

  it("mostra as notas e oferece só atributos não avaliados", async () => {
    mockApi({
      ...baseHandlers,
      "GET /player/1/attribute/": [{ attribute: PASS, value: 82 }],
      "GET /attribute/": [PASS, SPEED],
    })

    renderDetail()

    expect(
      await screen.findByRole("progressbar", { name: "Passe: 82 de 100" }),
    ).toBeInTheDocument()
    const select = screen.getByLabelText("Atributo")
    expect(within(select).queryByText("Passe")).not.toBeInTheDocument()
    expect(within(select).getByText("Velocidade")).toBeInTheDocument()
  })

  it("valida a nota entre 0 e 100 e envia a avaliação", async () => {
    const api = mockApi({
      ...baseHandlers,
      "GET /player/1/attribute/": [],
      "GET /attribute/": [SPEED],
      "POST /player/1/attribute/": () =>
        jsonResponse({ attribute: SPEED, value: 90 }, 201),
    })
    renderDetail()
    await screen.findByText("Nenhum atributo avaliado.")

    await userEvent.selectOptions(screen.getByLabelText("Atributo"), "31")
    await userEvent.type(screen.getByLabelText("Nota"), "150")
    await userEvent.click(screen.getByRole("button", { name: "Avaliar" }))

    expect(
      await screen.findByText("Informe uma nota de 0 a 100"),
    ).toBeInTheDocument()
    expect(api.find("POST", "/player/1/attribute/")).toBeUndefined()

    await userEvent.clear(screen.getByLabelText("Nota"))
    await userEvent.type(screen.getByLabelText("Nota"), "90")
    await userEvent.click(screen.getByRole("button", { name: "Avaliar" }))

    await waitFor(() =>
      expect(api.find("POST", "/player/1/attribute/")?.body).toEqual({
        attribute_id: 31,
        value: 90,
      }),
    )
  })

  it("edita uma nota existente", async () => {
    const api = mockApi({
      ...baseHandlers,
      "GET /player/1/attribute/": [{ attribute: PASS, value: 60 }],
      "GET /attribute/": [PASS],
      "PUT /player/1/attribute/30/": () =>
        jsonResponse({ attribute: PASS, value: 75 }),
    })
    renderDetail()

    await userEvent.click(
      await screen.findByRole("button", { name: "Editar nota de Passe" }),
    )
    const input = await screen.findByLabelText("Nota (0 a 100)")
    await userEvent.clear(input)
    await userEvent.type(input, "75")
    await userEvent.click(screen.getByRole("button", { name: "Salvar" }))

    await waitFor(() =>
      expect(api.find("PUT", "/player/1/attribute/30/")?.body).toEqual({
        value: 75,
      }),
    )
  })

  it("indica onde cadastrar atributos quando o catálogo está vazio", async () => {
    mockApi({ ...baseHandlers, ...NO_ATTRIBUTES })

    renderDetail()

    expect(
      await screen.findByRole("link", { name: "Atributos" }),
    ).toHaveAttribute("href", "/attributes")
  })
})
