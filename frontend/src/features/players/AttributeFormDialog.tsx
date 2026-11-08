import { zodResolver } from "@hookform/resolvers/zod"
import { useEffect } from "react"
import { useForm } from "react-hook-form"
import { toast } from "sonner"

import { FormDialog } from "@/components/common/FormDialog"
import { FormTextField } from "@/components/common/FormTextField"
import { applyApiErrors } from "@/lib/form-errors"

import { useCreateAttribute, useUpdateAttribute } from "./hooks"
import { attributeSchema, type AttributeValues } from "./schemas"
import type { Attribute } from "./types"

const ATTRIBUTE_FIELDS = ["name"] as const

type AttributeFormDialogProps = {
  open: boolean
  attribute: Attribute | null
  onOpenChange: (open: boolean) => void
}

export function AttributeFormDialog({
  open,
  attribute,
  onOpenChange,
}: AttributeFormDialogProps) {
  const createAttribute = useCreateAttribute()
  const updateAttribute = useUpdateAttribute()
  const form = useForm<AttributeValues>({
    resolver: zodResolver(attributeSchema),
    defaultValues: { name: "" },
  })

  useEffect(() => {
    if (open) {
      form.reset({ name: attribute?.name ?? "" })
    }
  }, [open, attribute, form])

  const onSubmit = form.handleSubmit(async (values) => {
    try {
      if (attribute === null) {
        await createAttribute.mutateAsync(values)
        toast.success("Atributo criado")
      } else {
        await updateAttribute.mutateAsync({ id: attribute.id, payload: values })
        toast.success("Atributo atualizado")
      }
      onOpenChange(false)
    } catch (error) {
      applyApiErrors(error, ATTRIBUTE_FIELDS, form.setError)
    }
  })

  return (
    <FormDialog
      open={open}
      title={attribute === null ? "Novo atributo" : "Editar atributo"}
      description="Atributos são avaliados com notas de 0 a 100 em cada jogador."
      pending={createAttribute.isPending || updateAttribute.isPending}
      rootError={form.formState.errors.root?.message}
      onSubmit={onSubmit}
      onOpenChange={onOpenChange}
    >
      <FormTextField
        control={form.control}
        name="name"
        label="Nome"
        id="attribute-name"
        autoFocus
      />
    </FormDialog>
  )
}
