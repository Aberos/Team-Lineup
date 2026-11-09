import { z } from "zod"

const SCRIPT_MAX_LENGTH = 10_000
const DESCRIPTION_MAX_LENGTH = 200

export const formulaSchema = z.object({
  script: z
    .string()
    .refine((value) => value.trim().length > 0, "Escreva o script da fórmula")
    .refine(
      (value) => value.length <= SCRIPT_MAX_LENGTH,
      "Use no máximo 10.000 caracteres",
    ),
  description: z
    .string()
    .trim()
    .max(DESCRIPTION_MAX_LENGTH, "Use no máximo 200 caracteres"),
})

export type FormulaValues = z.infer<typeof formulaSchema>
