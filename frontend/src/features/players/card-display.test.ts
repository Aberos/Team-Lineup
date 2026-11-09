import { describe, expect, it } from "vitest"

import { initialsOf, splitColumns, tierFor } from "./card-display"

describe("tierFor", () => {
  it("separa os níveis pelos limites da nota geral", () => {
    expect(tierFor(85).label).toBe("Elite")
    expect(tierFor(84).label).toBe("Destaque")
    expect(tierFor(70).label).toBe("Destaque")
    expect(tierFor(69).label).toBe("Base")
    expect(tierFor(null).label).toBe("Sem avaliação")
  })
})

describe("initialsOf", () => {
  it("usa as duas primeiras palavras em maiúsculas", () => {
    expect(initialsOf("ana  souza lima")).toBe("AS")
    expect(initialsOf("Bia")).toBe("B")
  })
})

describe("splitColumns", () => {
  it("divide os atributos em duas colunas, a primeira maior", () => {
    const attributes = ["A", "B", "C", "D", "E"].map((abbreviation) => ({
      abbreviation,
      name: abbreviation,
      value: 1,
    }))

    const [left, right] = splitColumns(attributes)

    expect(left.map((item) => item.abbreviation)).toEqual(["A", "B", "C"])
    expect(right.map((item) => item.abbreviation)).toEqual(["D", "E"])
  })
})
