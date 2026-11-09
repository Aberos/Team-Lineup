import {
  Controller,
  type Control,
  type FieldValues,
  type Path,
} from "react-hook-form"

import { Checkbox } from "@/components/ui/checkbox"
import { Field, FieldLabel } from "@/components/ui/field"

type FormCheckboxFieldProps<TInput extends FieldValues, TOutput> = {
  control: Control<TInput, unknown, TOutput>
  name: Path<TInput>
  label: string
  id: string
}

export function FormCheckboxField<TInput extends FieldValues, TOutput>({
  control,
  name,
  label,
  id,
}: FormCheckboxFieldProps<TInput, TOutput>) {
  return (
    <Controller
      name={name}
      control={control}
      render={({ field }) => (
        <Field orientation="horizontal">
          <Checkbox
            id={id}
            name={field.name}
            ref={field.ref}
            checked={field.value === true}
            onCheckedChange={(checked) => field.onChange(checked === true)}
            onBlur={field.onBlur}
          />
          <FieldLabel htmlFor={id} className="font-normal">
            {label}
          </FieldLabel>
        </Field>
      )}
    />
  )
}
