import { screen, within } from "@testing-library/react"
import { describe, expect, it } from "vitest"

import { renderWithProviders } from "@/test/render"

import { PlayerCardView } from "./PlayerCardView"
import type { PlayerCard } from "./types"

const ANA: PlayerCard = {
  id: 1,
  name: "Ana Souza",
  number: 10,
  overall: 88,
  photo_url: null,
  roles: [
    { id: 2, name: "MID", is_primary: true },
    { id: 3, name: "ATK", is_primary: false },
  ],
  card_attributes: [
    { abbreviation: "VEL", name: "Velocidade", value: 87 },
    { abbreviation: "FIN", name: "Finalização", value: 86 },
    { abbreviation: "PAS", name: "Passe", value: 91 },
    { abbreviation: "DRI", name: "Drible", value: 90 },
    { abbreviation: "DEF", name: "Defesa", value: null },
    { abbreviation: "FÍS", name: "Físico", value: 80 },
  ],
}

describe("PlayerCardView", () => {
  it("mostra nota, posição, número, atributos e nível", () => {
    renderWithProviders(<PlayerCardView player={ANA} />)

    const card = screen.getByRole("link", {
      name: "Ana Souza, geral 88, funções MID, ATK",
    })
    expect(card).toHaveAttribute("href", "/players/1")
    expect(within(card).getByText("88")).toBeInTheDocument()
    expect(within(card).getByText("MID")).toBeInTheDocument()
    expect(within(card).getByText("ATK")).toBeInTheDocument()
    expect(within(card).getByText("#10")).toBeInTheDocument()
    expect(within(card).getByText("Elite")).toBeInTheDocument()
    expect(within(card).getByText("AS")).toBeInTheDocument()
    expect(within(card).getByText("PAS")).toBeInTheDocument()
    expect(within(card).getByText("–")).toBeInTheDocument()
  })

  it("mostra carta sem avaliação para jogador sem notas", () => {
    renderWithProviders(
      <PlayerCardView
        player={{
          ...ANA,
          overall: null,
          roles: [],
          card_attributes: [],
        }}
      />,
    )

    const card = screen.getByRole("link", { name: "Ana Souza, geral sem avaliação" })
    expect(within(card).getByText("Sem avaliação")).toBeInTheDocument()
    expect(within(card).getAllByText("–")).toHaveLength(2)
  })

  it("usa a foto no lugar das iniciais", () => {
    const { container } = renderWithProviders(
      <PlayerCardView player={{ ...ANA, photo_url: "/media/players/ana.png" }} />,
    )

    expect(container.querySelector("img")).toHaveAttribute(
      "src",
      "/media/players/ana.png",
    )
    expect(screen.queryByText("AS")).not.toBeInTheDocument()
  })
})
