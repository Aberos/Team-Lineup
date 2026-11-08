import { screen, waitFor, within } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { afterEach, describe, expect, it, vi } from "vitest"

import { mockApi, type ApiHandlers } from "@/test/mock-api"
import { jsonResponse, renderWithProviders } from "@/test/render"

import { EventDetailPage } from "./EventDetailPage"

const EVENT = { id: 3, name: "Copa", date: "2026-05-01", location: "Arena" }
const ANA = { id: 1, name: "Ana", number: 10 }
const BIA = { id: 2, name: "Bia", number: 7 }
const TEAM_A = { id: 11, team_name: "Azul" }
const TEAM_B = { id: 12, team_name: "Branco" }

const BASE_HANDLERS: ApiHandlers = {
  "GET /event/3/": EVENT,
  "GET /event/3/participant/": [],
  "GET /event/3/team/": [],
  "GET /event/3/match/": [],
  "GET /player/": [ANA, BIA],
}

const renderDetail = () =>
  renderWithProviders(<EventDetailPage />, {
    path: "/events/:eventId",
    initialPath: "/events/3",
  })

describe("EventDetailPage", () => {
  afterEach(() => {
    vi.unstubAllGlobals()
  })

  it("mostra o evento e adiciona um participante", async () => {
    const api = mockApi({
      ...BASE_HANDLERS,
      "POST /event/3/participant/": () =>
        jsonResponse({ player: BIA, score: 0 }, 201),
    })
    renderDetail()

    expect(await screen.findByRole("heading", { name: "Copa" })).toBeInTheDocument()
    expect(screen.getByText("Arena")).toBeInTheDocument()
    await screen.findByText("Nenhum participante inscrito.")

    await userEvent.click(
      screen.getByRole("button", { name: "Adicionar participante" }),
    )
    await userEvent.selectOptions(screen.getByLabelText("Jogador"), "2")
    await userEvent.click(screen.getByRole("button", { name: "Adicionar" }))

    await waitFor(() =>
      expect(api.find("POST", "/event/3/participant/")?.body).toEqual({
        player_id: 2,
        score: 0,
      }),
    )
  })

  it("oferece para o time só participantes sem time", async () => {
    mockApi({
      ...BASE_HANDLERS,
      "GET /event/3/participant/": [
        { player: ANA, score: 0 },
        { player: BIA, score: 0 },
      ],
      "GET /event/3/team/": [TEAM_A, TEAM_B],
      "GET /event/3/team/11/member/": [{ player: ANA }],
      "GET /event/3/team/12/member/": [],
    })
    renderDetail()

    await userEvent.click(await screen.findByRole("tab", { name: "Times" }))

    const select = await screen.findByLabelText("Adicionar jogador", {
      selector: "#team-12-member",
    })
    expect(within(select).queryByText("10 - Ana")).not.toBeInTheDocument()
    expect(within(select).getByText("7 - Bia")).toBeInTheDocument()
  })

  it("exige dois times para criar partida", async () => {
    mockApi({ ...BASE_HANDLERS, "GET /event/3/team/": [TEAM_A] })
    renderDetail()

    await userEvent.click(await screen.findByRole("tab", { name: "Partidas" }))

    expect(
      await screen.findByText("Crie ao menos dois times para cadastrar partidas."),
    ).toBeInTheDocument()
    expect(screen.getByRole("button", { name: "Nova partida" })).toBeDisabled()
  })

  it("cria uma partida entre dois times", async () => {
    const api = mockApi({
      ...BASE_HANDLERS,
      "GET /event/3/team/": [TEAM_A, TEAM_B],
      "POST /event/3/match/": () =>
        jsonResponse(
          {
            id: 20,
            team_home: TEAM_A,
            team_away: TEAM_B,
            score_team_home: 2,
            score_team_away: 1,
            status: 2,
          },
          201,
        ),
    })
    renderDetail()

    await userEvent.click(await screen.findByRole("tab", { name: "Partidas" }))
    await userEvent.click(
      await screen.findByRole("button", { name: "Nova partida" }),
    )
    await userEvent.selectOptions(screen.getByLabelText("Mandante"), "11")
    await userEvent.selectOptions(screen.getByLabelText("Visitante"), "12")
    await userEvent.clear(screen.getByLabelText("Gols do mandante"))
    await userEvent.type(screen.getByLabelText("Gols do mandante"), "2")
    await userEvent.clear(screen.getByLabelText("Gols do visitante"))
    await userEvent.type(screen.getByLabelText("Gols do visitante"), "1")
    await userEvent.selectOptions(screen.getByLabelText("Situação"), "2")
    await userEvent.click(screen.getByRole("button", { name: "Salvar" }))

    await waitFor(() =>
      expect(api.find("POST", "/event/3/match/")?.body).toEqual({
        team_home_id: 11,
        team_away_id: 12,
        score_team_home: 2,
        score_team_away: 1,
        status: 2,
      }),
    )
  })

  it("mostra evento não encontrado", async () => {
    mockApi({
      ...BASE_HANDLERS,
      "GET /event/3/": () => jsonResponse({ detail: "Event not found." }, 404),
    })

    renderDetail()

    expect(await screen.findByText("Evento não encontrado.")).toBeInTheDocument()
  })
})
