import { screen, waitFor, within } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest"

import { jsonResponse, renderWithProviders } from "@/test/render"

import { RolesPage } from "./RolesPage"

describe("RolesPage", () => {
  const fetchMock = vi.fn<typeof fetch>()

  beforeEach(() => {
    vi.stubGlobal("fetch", fetchMock)
  })

  afterEach(() => {
    fetchMock.mockReset()
    vi.unstubAllGlobals()
  })

  it("lista as funções retornadas pela API", async () => {
    fetchMock.mockResolvedValue(
      jsonResponse([
        { id: 1, name: "Goleiro" },
        { id: 2, name: "Atacante" },
      ]),
    )

    renderWithProviders(<RolesPage />)

    expect(await screen.findByText("Goleiro")).toBeInTheDocument()
    expect(screen.getByText("Atacante")).toBeInTheDocument()
  })

  it("mostra estado vazio", async () => {
    fetchMock.mockResolvedValue(jsonResponse([]))

    renderWithProviders(<RolesPage />)

    expect(
      await screen.findByText("Nenhuma função cadastrada."),
    ).toBeInTheDocument()
  })

  it("mostra alerta quando a API falha", async () => {
    fetchMock.mockResolvedValue(jsonResponse({ detail: "erro" }, 500))

    renderWithProviders(<RolesPage />)

    expect(await screen.findByText("Erro ao carregar")).toBeInTheDocument()
  })

  it("cria uma função pelo diálogo", async () => {
    fetchMock
      .mockResolvedValueOnce(jsonResponse([]))
      .mockResolvedValueOnce(jsonResponse({ id: 3, name: "Zagueiro" }, 201))
      .mockResolvedValue(jsonResponse([{ id: 3, name: "Zagueiro" }]))

    renderWithProviders(<RolesPage />)
    await screen.findByText("Nenhuma função cadastrada.")

    await userEvent.click(screen.getByRole("button", { name: "Nova função" }))
    await userEvent.type(screen.getByLabelText("Nome"), "Zagueiro")
    await userEvent.click(screen.getByRole("button", { name: "Salvar" }))

    await waitFor(() =>
      expect(fetchMock).toHaveBeenCalledWith(
        "/api/v1/role/",
        expect.objectContaining({
          method: "POST",
          body: JSON.stringify({ name: "Zagueiro" }),
        }),
      ),
    )
    expect(await screen.findByText("Zagueiro")).toBeInTheDocument()
  })

  it("exclui uma função", async () => {
    fetchMock
      .mockResolvedValueOnce(jsonResponse([{ id: 1, name: "Goleiro" }]))
      .mockResolvedValueOnce(new Response(null, { status: 204 }))
      .mockResolvedValue(jsonResponse([]))

    renderWithProviders(<RolesPage />)

    await userEvent.click(
      await screen.findByRole("button", { name: "Excluir Goleiro" }),
    )
    const dialog = await screen.findByRole("alertdialog")
    await userEvent.click(within(dialog).getByRole("button", { name: "Excluir" }))

    expect(
      await screen.findByText("Nenhuma função cadastrada."),
    ).toBeInTheDocument()
    expect(fetchMock).toHaveBeenCalledWith(
      "/api/v1/role/1/",
      expect.objectContaining({ method: "DELETE" }),
    )
  })
})
