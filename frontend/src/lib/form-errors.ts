import type { FieldValues, Path, UseFormSetError } from "react-hook-form"

import { ApiError } from "@/lib/api-client"

const DEFAULT_MESSAGE = "Não foi possível concluir a operação."

type ErrorBody = Record<string, unknown>

function isErrorBody(value: unknown): value is ErrorBody {
  return typeof value === "object" && value !== null && !Array.isArray(value)
}

function firstMessage(value: unknown): string | null {
  if (typeof value === "string") {
    return value
  }
  if (Array.isArray(value) && typeof value[0] === "string") {
    return value[0]
  }
  return null
}

export function applyApiErrors<T extends FieldValues>(
  error: unknown,
  fields: ReadonlyArray<Path<T>>,
  setError: UseFormSetError<T>,
): void {
  const body = error instanceof ApiError ? error.body : null
  if (!isErrorBody(body)) {
    setError("root", { message: DEFAULT_MESSAGE })
    return
  }

  let hasFieldError = false
  for (const field of fields) {
    const message = firstMessage(body[field])
    if (message !== null) {
      setError(field, { message })
      hasFieldError = true
    }
  }

  const detail = firstMessage(body.detail ?? body.non_field_errors)
  if (detail !== null || !hasFieldError) {
    setError("root", { message: detail ?? DEFAULT_MESSAGE })
  }
}
