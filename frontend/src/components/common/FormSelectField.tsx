import {
  Controller,
  type Control,
  type FieldValues,
  type Path,
} from "react-hook-form"

import { Field, FieldError, FieldLabel } from "@/components/ui/field"
import {
  NativeSelect,
  NativeSelectOption,
} from "@/components/ui/native-select"

export type SelectOption = {
  value: string
  label: string
  disabled?: boolean
}

type FormSelectFieldProps<TInput extends FieldValues, TOutput> = {
  control: Control<TInput, unknown, TOutput>
  name: Path<TInput>
  label: string
  id: string
  options: ReadonlyArray<SelectOption>
  placeholder?: string
}

export function FormSelectField<TInput extends FieldValues, TOutput>({
  control,
  name,
  label,
  id,
  options,
  placeholder,
}: FormSelectFieldProps<TInput, TOutput>) {
  return (
    <Controller
      name={name}
      control={control}
      render={({ field, fieldState }) => (
        <Field data-invalid={fieldState.invalid}>
          <FieldLabel htmlFor={id}>{label}</FieldLabel>
          <NativeSelect
            name={field.name}
            ref={field.ref}
            value={String(field.value ?? "")}
            onChange={field.onChange}
            onBlur={field.onBlur}
            id={id}
            className="w-full"
            aria-invalid={fieldState.invalid}
          >
            {placeholder !== undefined && (
              <NativeSelectOption value="">{placeholder}</NativeSelectOption>
            )}
            {options.map((option) => (
              <NativeSelectOption
                key={option.value}
                value={option.value}
                disabled={option.disabled}
              >
                {option.label}
              </NativeSelectOption>
            ))}
          </NativeSelect>
          {fieldState.invalid && <FieldError errors={[fieldState.error]} />}
        </Field>
      )}
    />
  )
}
