import { zodResolver } from "@hookform/resolvers/zod"
import { useEffect } from "react"
import { useForm } from "react-hook-form"
import { toast } from "sonner"

import { FormDialog } from "@/components/common/FormDialog"
import { FormSelectField } from "@/components/common/FormSelectField"
import { FormTextField } from "@/components/common/FormTextField"
import { applyApiErrors } from "@/lib/form-errors"

import { useCreateAttribute, useUpdateAttribute } from "./hooks"
import {
  attributeSchema,
  type AttributeFormInput,
  type AttributeFormOutput,
} from "./schemas"
import { CARD_SLOTS, type Attribute } from "./types"

const ATTRIBUTE_FIELDS = ["name", "abbreviation", "card_order"] as const

function toFormValues(attribute: Attribute | null): AttributeFormInput {
  return {
    name: attribute?.name ?? "",
    abbreviation: attribute?.abbreviation ?? "",
    card_order:
      attribute?.card_order === null || attribute?.card_order === undefined
        ? ""
        : String(attribute.card_order),
  }
}

function cardSlotOptions(
  attributes: ReadonlyArray<Attribute>,
  editingId: number | null,
) {
  const occupants = new Map(
    attributes
      .filter((item) => item.card_order !== null && item.id !== editingId)
      .map((item) => [item.card_order, item.abbreviation]),
  )
  return [
    { value: "", label: "Não exibir na carta" },
    ...CARD_SLOTS.map((slot) => {
      const occupant = occupants.get(slot)
      return {
        value: String(slot),
        label: occupant
          ? `Posição ${slot} (ocupada por ${occupant})`
          : `Posição ${slot}`,
        disabled: occupant !== undefined,
      }
    }),
  ]
}

type AttributeFormDialogProps = {
  open: boolean
  attribute: Attribute | null
  attributes: ReadonlyArray<Attribute>
  onOpenChange: (open: boolean) => void
}

export function AttributeFormDialog({
  open,
  attribute,
  attributes,
  onOpenChange,
}: AttributeFormDialogProps) {
  const createAttribute = useCreateAttribute()
  const updateAttribute = useUpdateAttribute()
  const form = useForm<AttributeFormInput, unknown, AttributeFormOutput>({
    resolver: zodResolver(attributeSchema),
    defaultValues: toFormValues(null),
  })

  useEffect(() => {
    if (open) {
      form.reset(toFormValues(attribute))
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
      description="Atributos são avaliados com notas de 0 a 100. Até 6 aparecem na carta do jogador."
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
      <div className="grid gap-4 sm:grid-cols-2">
        <FormTextField
          control={form.control}
          name="abbreviation"
          label="Sigla na carta"
          id="attribute-abbreviation"
        />
        <FormSelectField
          control={form.control}
          name="card_order"
          label="Posição na carta"
          id="attribute-card-order"
          options={cardSlotOptions(attributes, attribute?.id ?? null)}
        />
      </div>
    </FormDialog>
  )
}
