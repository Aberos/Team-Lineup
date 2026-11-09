import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"

import { formulaApi } from "./api"
import type { FormulaPayload } from "./types"

const FORMULA_KEY = ["formula"] as const
const FORMULA_LIST_KEY = [...FORMULA_KEY, "list"] as const
const ACTIVE_FORMULA_KEY = [...FORMULA_KEY, "active"] as const
export const PREVIEW_LIMIT = 10

function useInvalidateFormulas(includePlayers: boolean) {
  const queryClient = useQueryClient()
  return () =>
    Promise.all([
      queryClient.invalidateQueries({ queryKey: FORMULA_KEY }),
      includePlayers
        ? queryClient.invalidateQueries({ queryKey: ["players"] })
        : Promise.resolve(),
    ])
}

export function useFormulas() {
  return useQuery({ queryKey: FORMULA_LIST_KEY, queryFn: formulaApi.list })
}

export function useActiveFormula() {
  return useQuery({ queryKey: ACTIVE_FORMULA_KEY, queryFn: formulaApi.active })
}

export function useCreateFormula() {
  const invalidate = useInvalidateFormulas(false)
  return useMutation({
    mutationFn: (payload: FormulaPayload) => formulaApi.create(payload),
    onSuccess: invalidate,
  })
}

export function usePreviewFormula() {
  return useMutation({
    mutationFn: (script: string) => formulaApi.preview(script, PREVIEW_LIMIT),
  })
}

export function useActivateFormula() {
  const invalidate = useInvalidateFormulas(true)
  return useMutation({
    mutationFn: (id: number) => formulaApi.activate(id),
    onSuccess: invalidate,
  })
}

export function useDeactivateFormula() {
  const invalidate = useInvalidateFormulas(true)
  return useMutation({
    mutationFn: () => formulaApi.deactivate(),
    onSuccess: invalidate,
  })
}

export function useDeleteFormula() {
  const invalidate = useInvalidateFormulas(false)
  return useMutation({
    mutationFn: (id: number) => formulaApi.remove(id),
    onSuccess: invalidate,
  })
}
