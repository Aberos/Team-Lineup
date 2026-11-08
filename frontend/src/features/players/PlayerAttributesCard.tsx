import { zodResolver } from "@hookform/resolvers/zod"
import { Pencil, Plus, Trash2 } from "lucide-react"
import { useState } from "react"
import { useForm } from "react-hook-form"
import { Link } from "react-router"
import { toast } from "sonner"

import { EmptyState } from "@/components/common/EmptyState"
import { FormSelectField } from "@/components/common/FormSelectField"
import { FormTextField } from "@/components/common/FormTextField"
import { Button } from "@/components/ui/button"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { FieldError } from "@/components/ui/field"
import { Progress } from "@/components/ui/progress"
import { Skeleton } from "@/components/ui/skeleton"
import { applyApiErrors } from "@/lib/form-errors"

import {
  useAttributes,
  usePlayerAttributes,
  useRatePlayer,
  useRemoveRating,
} from "./hooks"
import { RatingDialog } from "./RatingDialog"
import {
  ratingSchema,
  type RatingFormInput,
  type RatingFormOutput,
} from "./schemas"
import type { PlayerAttribute } from "./types"

const RATING_FIELDS = ["attribute_id", "value"] as const

const EMPTY_VALUES: RatingFormInput = { attribute_id: "", value: "" }

type PlayerAttributesCardProps = {
  playerId: number
}

export function PlayerAttributesCard({ playerId }: PlayerAttributesCardProps) {
  const ratings = usePlayerAttributes(playerId)
  const attributes = useAttributes()
  const ratePlayer = useRatePlayer(playerId)
  const removeRating = useRemoveRating(playerId)
  const [editing, setEditing] = useState<PlayerAttribute | null>(null)
  const form = useForm<RatingFormInput, unknown, RatingFormOutput>({
    resolver: zodResolver(ratingSchema),
    defaultValues: EMPTY_VALUES,
  })

  const ratedIds = new Set(ratings.data?.map((rating) => rating.attribute.id))
  const availableOptions = (attributes.data ?? [])
    .filter((attribute) => !ratedIds.has(attribute.id))
    .map((attribute) => ({
      value: String(attribute.id),
      label: attribute.name,
    }))
  const hasCatalog = attributes.isSuccess && attributes.data.length > 0

  const onSubmit = form.handleSubmit(
    async ({ attribute_id: attributeId, value }) => {
      try {
        await ratePlayer.mutateAsync({ attributeId, value })
        form.reset(EMPTY_VALUES)
        toast.success("Nota adicionada")
      } catch (error) {
        applyApiErrors(error, RATING_FIELDS, form.setError)
      }
    },
  )

  const handleRemove = (rating: PlayerAttribute) => {
    removeRating.mutate(rating.attribute.id, {
      onSuccess: () => toast.success(`Nota de "${rating.attribute.name}" removida`),
      onError: () => toast.error("Não foi possível remover a nota."),
    })
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Atributos</CardTitle>
        <CardDescription>Notas de 0 a 100 em cada habilidade.</CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        {ratings.isPending && <Skeleton className="h-16 w-full" />}
        {ratings.isError && (
          <p className="text-sm text-destructive">
            Não foi possível carregar os atributos do jogador.
          </p>
        )}
        {ratings.isSuccess && ratings.data.length === 0 && (
          <EmptyState message="Nenhum atributo avaliado." />
        )}
        {ratings.isSuccess && ratings.data.length > 0 && (
          <ul className="space-y-3">
            {ratings.data.map((rating) => (
              <li key={rating.attribute.id} className="flex items-center gap-3">
                <div className="min-w-0 flex-1 space-y-1">
                  <div className="flex items-baseline justify-between gap-2 text-sm">
                    <span className="truncate">{rating.attribute.name}</span>
                    <span className="font-semibold tabular-nums">
                      {rating.value}
                    </span>
                  </div>
                  <Progress
                    value={rating.value}
                    aria-label={`${rating.attribute.name}: ${rating.value} de 100`}
                  />
                </div>
                <div className="flex shrink-0">
                  <Button
                    variant="ghost"
                    size="icon"
                    aria-label={`Editar nota de ${rating.attribute.name}`}
                    onClick={() => setEditing(rating)}
                  >
                    <Pencil />
                  </Button>
                  <Button
                    variant="ghost"
                    size="icon"
                    aria-label={`Remover nota de ${rating.attribute.name}`}
                    disabled={removeRating.isPending}
                    onClick={() => handleRemove(rating)}
                  >
                    <Trash2 />
                  </Button>
                </div>
              </li>
            ))}
          </ul>
        )}
        {attributes.isSuccess && !hasCatalog ? (
          <p className="text-sm text-muted-foreground">
            Cadastre atributos em{" "}
            <Link to="/attributes" className="underline underline-offset-4">
              Atributos
            </Link>{" "}
            para avaliar o jogador.
          </p>
        ) : (
          <form
            onSubmit={onSubmit}
            noValidate
            className="grid gap-2 sm:grid-cols-[1fr_8rem_auto] sm:items-end"
          >
            <FormSelectField
              control={form.control}
              name="attribute_id"
              label="Atributo"
              id="rating-attribute"
              options={availableOptions}
              placeholder={
                availableOptions.length === 0 ? "Todos avaliados" : "Selecione"
              }
            />
            <FormTextField
              control={form.control}
              name="value"
              label="Nota"
              id="rating-new-value"
              inputMode="numeric"
            />
            <Button
              type="submit"
              disabled={ratePlayer.isPending || availableOptions.length === 0}
            >
              <Plus />
              Avaliar
            </Button>
          </form>
        )}
        {form.formState.errors.root && (
          <FieldError>{form.formState.errors.root.message}</FieldError>
        )}
      </CardContent>
      <RatingDialog
        playerId={playerId}
        rating={editing}
        onOpenChange={(open) => {
          if (!open) {
            setEditing(null)
          }
        }}
      />
    </Card>
  )
}
