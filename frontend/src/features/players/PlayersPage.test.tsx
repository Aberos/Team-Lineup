import { screen, waitFor } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { afterEach, describe, expect, it, vi } from "vitest"

import { mockApi } from "@/test/mock-api"
import { jsonResponse, renderWithProviders } from "@/test/render"

import { PlayersPage } from "./PlayersPage"

const ANA = {
  id: 1,
  name: "Ana Souza",
  birthday: "1995-04-10",
  phone: "11999990000",
  email: "ana@example.com",
  number: 10,
}

describe("PlayersPage", () => {
  afterEach(() => {
    vi.unstubAllGlobals()
  })

  it("lista os jogadores com link para o detalhe", async () => {
    mockApi({ "GET /player/": [{ id: 1, name: "Ana Souza", number: 10 }] })

    renderWithProviders(<PlayersPage />)

    const link = await screen.findByRole("link", { name: "Ana Souza" })
    expect(link).toHaveAttribute("href", "/players/1")
  })

  it("mostra estado vazio", async () => {
    mockApi({ "GET /player/": [] })

    renderWithProviders(<PlayersPage />)

    expect(
      await screen.findByText("Nenhum jogador cadastrado."),
    ).toBeInTheDocument()
  })

  it("valida o formulário antes de enviar", async () => {
    const api = mockApi({ "GET /player/": [] })
    renderWithProviders(<PlayersPage />)
    await screen.findByText("Nenhum jogador cadastrado.")

    await userEvent.click(screen.getByRole("button", { name: "Novo jogador" }))
    await userEvent.type(screen.getByLabelText("E-mail"), "invalido")
    await userEvent.type(screen.getByLabelText("Número"), "-3")
    await userEvent.click(screen.getByRole("button", { name: "Salvar" }))

    expect(await screen.findByText("Informe o nome")).toBeInTheDocument()
    expect(screen.getByText("Informe um e-mail válido")).toBeInTheDocument()
    expect(
      screen.getByText("Informe um número inteiro positivo"),
    ).toBeInTheDocument()
    expect(api.find("POST", "/player/")).toBeUndefined()
  })

  it("cadastra um jogador e mostra erro de e-mail duplicado", async () => {
    let attempts = 0
    const api = mockApi({
      "GET /player/": [],
      "POST /player/": () => {
        attempts += 1
        return attempts === 1
          ? jsonResponse(
              { email: ["A player with this email already exists."] },
              409,
            )
          : jsonResponse(ANA, 201)
      },
    })
    renderWithProviders(<PlayersPage />)
    await screen.findByText("Nenhum jogador cadastrado.")

    await userEvent.click(screen.getByRole("button", { name: "Novo jogador" }))
    await userEvent.type(screen.getByLabelText("Nome"), "Ana Souza")
    await userEvent.type(screen.getByLabelText("Nascimento"), "1995-04-10")
    await userEvent.type(screen.getByLabelText("Número"), "10")
    await userEvent.type(screen.getByLabelText("Telefone"), "11999990000")
    await userEvent.type(screen.getByLabelText("E-mail"), "ana@example.com")
    await userEvent.click(screen.getByRole("button", { name: "Salvar" }))

    expect(
      await screen.findByText("A player with this email already exists."),
    ).toBeInTheDocument()

    await userEvent.click(screen.getByRole("button", { name: "Salvar" }))

    await waitFor(() =>
      expect(screen.queryByRole("dialog")).not.toBeInTheDocument(),
    )
    expect(api.find("POST", "/player/")?.body).toEqual({
      name: "Ana Souza",
      birthday: "1995-04-10",
      phone: "11999990000",
      email: "ana@example.com",
      number: 10,
    })
  })
})
