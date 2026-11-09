import { apiRequest } from "@/lib/api-client"

import type {
  ActiveFormula,
  FormulaPayload,
  FormulaPreviewRow,
  OverallFormula,
} from "./types"

const FORMULA_PATH = "/overall-formula/"

export const formulaApi = {
  list: () => apiRequest<OverallFormula[]>(FORMULA_PATH),
  active: () => apiRequest<ActiveFormula>(`${FORMULA_PATH}active/`),
  deactivate: () =>
    apiRequest<null>(`${FORMULA_PATH}active/`, { method: "DELETE" }),
  create: (payload: FormulaPayload) =>
    apiRequest<OverallFormula>(FORMULA_PATH, { method: "POST", body: payload }),
  preview: (script: string, limit: number) =>
    apiRequest<FormulaPreviewRow[]>(`${FORMULA_PATH}preview/`, {
      method: "POST",
      body: { script, limit },
    }),
  activate: (id: number) =>
    apiRequest<OverallFormula>(`${FORMULA_PATH}${id}/activate/`, {
      method: "POST",
    }),
  remove: (id: number) =>
    apiRequest<null>(`${FORMULA_PATH}${id}/`, { method: "DELETE" }),
}
