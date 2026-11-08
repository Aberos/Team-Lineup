import { screen } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { afterEach, describe, expect, it, vi } from "vitest"

import { mockApi } from "@/test/mock-api"
import { jsonResponse, renderWithProviders } from "@/test/render"

import { EventsPage } from "./EventsPage"

const COPA = { id: 3, name: "Copa", date: "2026-05-01", location: "Arena" }

describe("EventsPage", () => {
  afterEach(() => {
    vi.unstubAllGlobals()
  })

  it("lista os eventos com data formatada", async () => {
    mockApi({ "GET /event/": [COPA] })

    renderWithProviders(<EventsPage />, { path: "/events" })

    expect(await screen.findByRole("link", { name: "Copa" })).toHaveAttribute(
      "href",
      "/events/3",
    )
    expect(screen.getByText("01/05/2026")).toBeInTheDocument()
  })

  it("cria um evento e abre o detalhe", async () => {
    const api = mockApi({
      "GET /event/": [],
      "POST /event/": () => jsonResponse(COPA, 201),
    })
    renderWithProviders(<EventsPage />, {
      path: "/events",
      extraRoutes: [{ path: "/events/:eventId", element: <p>Detalhe</p> }],
    })
    await screen.findByText("Nenhum evento cadastrado.")

    await userEvent.click(screen.getByRole("button", { name: "Novo evento" }))
    await userEvent.type(screen.getByLabelText("Nome"), "Copa")
    await userEvent.type(screen.getByLabelText("Data"), "2026-05-01")
    await userEvent.type(screen.getByLabelText("Local"), "Arena")
    await userEvent.click(screen.getByRole("button", { name: "Salvar" }))

    expect(await screen.findByText("Detalhe")).toBeInTheDocument()
    expect(api.find("POST", "/event/")?.body).toEqual({
      name: "Copa",
      date: "2026-05-01",
      location: "Arena",
    })
  })
})
