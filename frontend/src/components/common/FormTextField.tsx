import type { HTMLInputTypeAttribute } from "react"
import {
  Controller,
  type Control,
  type FieldValues,
  type Path,
} from "react-hook-form"

import { Field, FieldError, FieldLabel } from "@/components/ui/field"
import { Input } from "@/components/ui/input"

type FormTextFieldProps<TInput extends FieldValues, TOutput> = {
  control: Control<TInput, unknown, TOutput>
  name: Path<TInput>
  label: string
  id: string
  type?: HTMLInputTypeAttribute
  autoComplete?: string
  inputMode?: "numeric" | "tel" | "email" | "text"
  autoFocus?: boolean
}

export function FormTextField<TInput extends FieldValues, TOutput>({
  control,
  name,
  label,
  id,
  type = "text",
  autoComplete,
  inputMode,
  autoFocus,
}: FormTextFieldProps<TInput, TOutput>) {
  return (
    <Controller
      name={name}
      control={control}
      render={({ field, fieldState }) => (
        <Field data-invalid={fieldState.invalid}>
          <FieldLabel htmlFor={id}>{label}</FieldLabel>
          <Input
            name={field.name}
            ref={field.ref}
            value={String(field.value ?? "")}
            onChange={field.onChange}
            onBlur={field.onBlur}
            id={id}
            type={type}
            autoComplete={autoComplete}
            inputMode={inputMode}
            autoFocus={autoFocus}
            aria-invalid={fieldState.invalid}
          />
          {fieldState.invalid && <FieldError errors={[fieldState.error]} />}
        </Field>
      )}
    />
  )
}
