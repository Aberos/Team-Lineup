export type OverallFormula = {
  id: number
  script: string
  description: string
  is_active: boolean
  created_at: string
  created_by: string | null
}

export type ActiveFormula = { formula: OverallFormula | null }

export type FormulaPayload = { script: string; description: string }

export type FormulaPreviewRow = {
  player_id: number
  player_name: string
  current_overall: number | null
  new_overall: number | null
  error: string | null
}

export type FormulaFailure = {
  player_id: number
  player_name: string
  error: string
}

export type FormulaActivationErrorBody = {
  detail: string
  failures: FormulaFailure[]
}
