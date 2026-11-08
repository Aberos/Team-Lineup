import { describe, expect, it } from "vitest"

import { matchSchema } from "./schemas"

const VALID = {
  team_home_id: "1",
  team_away_id: "2",
  score_team_home: "3",
  score_team_away: "0",
  status: "1",
}

describe("matchSchema", () => {
  it("converte os campos para o payload da API", () => {
    expect(matchSchema.parse(VALID)).toEqual({
      team_home_id: 1,
      team_away_id: 2,
      score_team_home: 3,
      score_team_away: 0,
      status: 1,
    })
  })

  it("rejeita times iguais, placar negativo e status inválido", () => {
    const invalid = [
      { ...VALID, team_away_id: "1" },
      { ...VALID, score_team_home: "-1" },
      { ...VALID, status: "9" },
    ]

    for (const values of invalid) {
      expect(matchSchema.safeParse(values).success).toBe(false)
    }
  })
})
