import { insertNewlineAndIndent } from "@codemirror/commands"
import { EditorView } from "@codemirror/view"
import { act, screen, waitFor, within } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { afterEach, describe, expect, it, vi } from "vitest"

import { mockApi, type ApiHandlers } from "@/test/mock-api"
import { jsonResponse, noContent, renderWithProviders } from "@/test/render"

import { FormulaPage } from "./FormulaPage"

const SAVED = {
  id: 4,
  script: "function overall(notas) return notas.PAS end",
  description: "Só passe",
  is_active: false,
  created_at: "2026-11-09T12:00:00Z",
  created_by: "admin",
}

const BASE: ApiHandlers = {
  "GET /overall-formula/active/": { formula: null },
  "GET /overall-formula/": [],
}

describe("FormulaPage", () => {
  afterEach(() => {
    vi.unstubAllGlobals()
  })

  it("mostra a média simples e o modelo no editor", async () => {
    mockApi(BASE)

    renderWithProviders(<FormulaPage />)

    expect(await screen.findByText("Média simples")).toBeInTheDocument()
    expect(
      await screen.findByRole("textbox", { name: "Script Lua" }),
    ).toHaveTextContent("function overall(notas, funcoes, principal)")
    expect(
      screen.getByText("Nenhuma versão salva. A média simples está em uso."),
    ).toBeInTheDocument()
  })

  it("testa o script e mostra o resultado por jogador", async () => {
    const api = mockApi({
      ...BASE,
      "POST /overall-formula/preview/": [
        {
          player_id: 1,
          player_name: "Ana",
          current_overall: 70,
          new_overall: 82,
          error: null,
        },
        {
          player_id: 2,
          player_name: "Bia",
          current_overall: null,
          new_overall: null,
          error: "formula:3: falhou",
        },
      ],
    })
    renderWithProviders(<FormulaPage />)

    await userEvent.click(
      await screen.findByRole("button", { name: "Testar com jogadores" }),
    )

    expect(await screen.findByText("82")).toBeInTheDocument()
    expect(screen.getByText("formula:3: falhou")).toBeInTheDocument()
    const call = api.find("POST", "/overall-formula/preview/")
    expect(call?.body).toMatchObject({ limit: 10 })
  })

  it("salva uma versão e mostra erro de script no campo", async () => {
    let attempts = 0
    const api = mockApi({
      ...BASE,
      "POST /overall-formula/": () => {
        attempts += 1
        return attempts === 1
          ? jsonResponse({ script: ["formula:1: unexpected symbol"] }, 400)
          : jsonResponse(SAVED, 201)
      },
    })
    renderWithProviders(<FormulaPage />)

    const description = await screen.findByLabelText("Descrição da versão")
    await userEvent.type(description, "Só passe")
    await userEvent.click(screen.getByRole("button", { name: "Salvar versão" }))

    expect(
      await screen.findByText("formula:1: unexpected symbol"),
    ).toBeInTheDocument()

    await userEvent.click(screen.getByRole("button", { name: "Salvar versão" }))

    await waitFor(() => expect(attempts).toBe(2))
    expect(api.find("POST", "/overall-formula/")?.body).toMatchObject({
      description: "Só passe",
    })
  })

  it("lista as falhas quando a ativação é recusada", async () => {
    mockApi({
      ...BASE,
      "GET /overall-formula/": [SAVED],
      "POST /overall-formula/4/activate/": () =>
        jsonResponse(
          {
            detail: "The formula failed for some players.",
            failures: [{ player_id: 1, player_name: "Ana", error: "sem DEF" }],
          },
          409,
        ),
    })
    renderWithProviders(<FormulaPage />)

    await userEvent.click(
      await screen.findByRole("button", { name: "Ativar versão 4" }),
    )

    expect(
      await screen.findByText("A fórmula #4 falhou para alguns jogadores"),
    ).toBeInTheDocument()
    expect(screen.getByText("Ana: sem DEF")).toBeInTheDocument()
  })

  it("abre uma versão no editor", async () => {
    mockApi({ ...BASE, "GET /overall-formula/": [SAVED] })
    renderWithProviders(<FormulaPage />)

    await userEvent.click(
      await screen.findByRole("button", { name: "Abrir versão 4 no editor" }),
    )

    await waitFor(() =>
      expect(
        screen.getByRole("textbox", { name: "Script Lua" }),
      ).toHaveTextContent(SAVED.script),
    )
  })

  it("volta para a média simples após confirmação", async () => {
    const api = mockApi({
      "GET /overall-formula/active/": {
        formula: { ...SAVED, is_active: true },
      },
      "GET /overall-formula/": [{ ...SAVED, is_active: true }],
      "DELETE /overall-formula/active/": () => noContent(),
    })
    renderWithProviders(<FormulaPage />)

    expect(await screen.findByText("Fórmula #4")).toBeInTheDocument()
    expect(screen.getByText("Em uso")).toBeInTheDocument()
    await userEvent.click(
      screen.getByRole("button", { name: "Usar média simples" }),
    )
    const dialog = await screen.findByRole("alertdialog")
    await userEvent.click(
      within(dialog).getByRole("button", { name: "Usar média simples" }),
    )

    await waitFor(() =>
      expect(api.find("DELETE", "/overall-formula/active/")).toBeDefined(),
    )
  })

  it("edita o script com indentação automática", async () => {
    const api = mockApi({
      ...BASE,
      "POST /overall-formula/preview/": [],
    })
    renderWithProviders(<FormulaPage />)
    const editor = await screen.findByRole("textbox", { name: "Script Lua" })
    const view = EditorView.findFromDOM(editor)
    if (view === null) {
      throw new Error("Editor não encontrado")
    }

    act(() => {
      view.dispatch({
        changes: {
          from: 0,
          to: view.state.doc.length,
          insert: "function overall(notas)",
        },
        selection: { anchor: "function overall(notas)".length },
      })
      insertNewlineAndIndent(view)
      view.dispatch(view.state.replaceSelection("return notas.VEL"))
    })
    await userEvent.click(
      screen.getByRole("button", { name: "Testar com jogadores" }),
    )

    await waitFor(() =>
      expect(api.find("POST", "/overall-formula/preview/")?.body).toEqual({
        script: "function overall(notas)\n  return notas.VEL",
        limit: 10,
      }),
    )
  })
})

