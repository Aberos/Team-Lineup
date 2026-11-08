import { screen, waitFor, within } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { afterEach, describe, expect, it, vi } from "vitest"

import { mockApi } from "@/test/mock-api"
import { jsonResponse, noContent, renderWithProviders } from "@/test/render"

import { AttributesPage } from "./AttributesPage"

describe("AttributesPage", () => {
  afterEach(() => {
    vi.unstubAllGlobals()
  })

  it("lista os atributos", async () => {
    mockApi({ "GET /attribute/": [{ id: 1, name: "Passe" }] })

    renderWithProviders(<AttributesPage />)

    expect(await screen.findByText("Passe")).toBeInTheDocument()
  })

  it("mostra o erro de nome duplicado no campo", async () => {
    mockApi({
      "GET /attribute/": [],
      "POST /attribute/": () =>
        jsonResponse(
          { name: ["An attribute with this name already exists."] },
          409,
        ),
    })
    renderWithProviders(<AttributesPage />)
    await screen.findByText("Nenhum atributo cadastrado.")

    await userEvent.click(screen.getByRole("button", { name: "Novo atributo" }))
    await userEvent.type(screen.getByLabelText("Nome"), "Passe")
    await userEvent.click(screen.getByRole("button", { name: "Salvar" }))

    expect(
      await screen.findByText("An attribute with this name already exists."),
    ).toBeInTheDocument()
  })

  it("exclui um atributo após confirmação", async () => {
    let deleted = false
    const api = mockApi({
      "GET /attribute/": () =>
        jsonResponse(deleted ? [] : [{ id: 1, name: "Passe" }]),
      "DELETE /attribute/1/": () => {
        deleted = true
        return noContent()
      },
    })
    renderWithProviders(<AttributesPage />)

    await userEvent.click(
      await screen.findByRole("button", { name: "Excluir Passe" }),
    )
    const dialog = await screen.findByRole("alertdialog")
    await userEvent.click(within(dialog).getByRole("button", { name: "Excluir" }))

    await waitFor(() =>
      expect(screen.getByText("Nenhum atributo cadastrado.")).toBeInTheDocument(),
    )
    expect(api.find("DELETE", "/attribute/1/")).toBeDefined()
  })
})
