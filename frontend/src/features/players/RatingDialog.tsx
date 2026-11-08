import { zodResolver } from "@hookform/resolvers/zod"
import { useEffect } from "react"
import { useForm } from "react-hook-form"
import { toast } from "sonner"

import { FormDialog } from "@/components/common/FormDialog"
import { FormTextField } from "@/components/common/FormTextField"
import { applyApiErrors } from "@/lib/form-errors"

import { useUpdateRating } from "./hooks"
import {
  ratingValueSchema,
  type RatingValueFormInput,
  type RatingValueFormOutput,
} from "./schemas"
import type { PlayerAttribute } from "./types"

const RATING_FIELDS = ["value"] as const

type RatingDialogProps = {
  playerId: number
  rating: PlayerAttribute | null
  onOpenChange: (open: boolean) => void
}

export function RatingDialog({
  playerId,
  rating,
  onOpenChange,
}: RatingDialogProps) {
  const updateRating = useUpdateRating(playerId)
  const form = useForm<RatingValueFormInput, unknown, RatingValueFormOutput>({
    resolver: zodResolver(ratingValueSchema),
    defaultValues: { value: "" },
  })

  useEffect(() => {
    if (rating !== null) {
      form.reset({ value: String(rating.value) })
    }
  }, [rating, form])

  const onSubmit = form.handleSubmit(async ({ value }) => {
    if (rating === null) {
      return
    }
    try {
      await updateRating.mutateAsync({
        attributeId: rating.attribute.id,
        value,
      })
      toast.success("Nota atualizada")
      onOpenChange(false)
    } catch (error) {
      applyApiErrors(error, RATING_FIELDS, form.setError)
    }
  })

  return (
    <FormDialog
      open={rating !== null}
      title="Editar nota"
      description={rating?.attribute.name ?? ""}
      pending={updateRating.isPending}
      rootError={form.formState.errors.root?.message}
      onSubmit={onSubmit}
      onOpenChange={onOpenChange}
    >
      <FormTextField
        control={form.control}
        name="value"
        label="Nota (0 a 100)"
        id="rating-value"
        inputMode="numeric"
        autoFocus
      />
    </FormDialog>
  )
}
