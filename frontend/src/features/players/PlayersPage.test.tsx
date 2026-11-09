import { screen, waitFor } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { afterEach, describe, expect, it, vi } from "vitest"

import { mockApi, page } from "@/test/mock-api"
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

const CARD = {
  id: 1,
  name: "Ana Souza",
  number: 10,
  overall: 88,
  photo_url: null,
  roles: [{ id: 3, name: "MID", is_primary: true }],
  card_attributes: [],
}

describe("PlayersPage", () => {
  afterEach(() => {
    vi.unstubAllGlobals()
  })

  it("lista os jogadores com link para o detalhe", async () => {
    mockApi({ "GET /role/": [], "GET /player/": page([CARD]) })

    renderWithProviders(<PlayersPage />)

    const link = await screen.findByRole("link", {
      name: "Ana Souza, geral 88, funções MID",
    })
    expect(link).toHaveAttribute("href", "/players/1")
  })

  it("mostra estado vazio", async () => {
    mockApi({ "GET /role/": [], "GET /player/": page([]) })

    renderWithProviders(<PlayersPage />)

    expect(
      await screen.findByText("Nenhum jogador cadastrado."),
    ).toBeInTheDocument()
  })

  it("valida o formulário antes de enviar", async () => {
    const api = mockApi({ "GET /role/": [], "GET /player/": page([]) })
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
      "GET /role/": [],
      "GET /player/": page([]),
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

  it("mostra nota geral e função principal", async () => {
    mockApi({ "GET /role/": [], "GET /player/": page([CARD]) })

    renderWithProviders(<PlayersPage />)

    expect(await screen.findByText("88")).toBeInTheDocument()
    expect(screen.getByText("MID")).toBeInTheDocument()
  })

  it("carrega a próxima página", async () => {
    const api = mockApi({
      "GET /role/": [],
      "GET /player/": ({ query }) =>
        jsonResponse(
          query.get("page") === "2"
            ? { ...page([{ ...CARD, id: 2, name: "Bia" }]), page: 2, count: 2 }
            : {
                ...page([CARD]),
                count: 2,
                next: "/api/v1/player/?page=2",
              },
        ),
    })
    renderWithProviders(<PlayersPage />)

    await userEvent.click(
      await screen.findByRole("button", { name: "Carregar mais" }),
    )

    expect(await screen.findByText("Bia")).toBeInTheDocument()
    expect(screen.getByText("Ana Souza")).toBeInTheDocument()
    expect(
      api.calls.filter((call) => call.path === "/player/").at(-1)?.query.get(
        "page",
      ),
    ).toBe("2")
  })

  it("envia busca, função e ordenação para a API", async () => {
    const api = mockApi({
      "GET /role/": [{ id: 3, name: "MID" }],
      "GET /player/": page([]),
    })
    renderWithProviders(<PlayersPage />)
    await screen.findByText("Nenhum jogador cadastrado.")
    await screen.findByRole("option", { name: "MID" })

    await userEvent.selectOptions(screen.getByLabelText("Função"), "3")
    await userEvent.selectOptions(
      screen.getByLabelText("Ordenar por"),
      "-overall",
    )
    await userEvent.type(screen.getByLabelText("Buscar"), "ana")

    await waitFor(() => {
      const query = api.calls.filter((call) => call.path === "/player/").at(-1)
        ?.query
      expect(query?.get("search")).toBe("ana")
      expect(query?.get("role")).toBe("3")
      expect(query?.get("ordering")).toBe("-overall")
    })
  })
})
