import { zodResolver } from "@hookform/resolvers/zod"
import { useEffect, useState } from "react"
import { type Control, useForm } from "react-hook-form"
import { toast } from "sonner"

import { FormDialog } from "@/components/common/FormDialog"
import { FormSelectField } from "@/components/common/FormSelectField"
import { FormTextField } from "@/components/common/FormTextField"
import { Field, FieldDescription, FieldLabel } from "@/components/ui/field"
import { Input } from "@/components/ui/input"
import { usePlayerSearch } from "@/features/players/hooks"
import { applyApiErrors } from "@/lib/form-errors"
import { useDebouncedValue } from "@/lib/use-debounced-value"

import { useAddParticipant } from "./hooks"
import {
  participantSchema,
  type ParticipantFormInput,
  type ParticipantFormOutput,
} from "./schemas"

const PARTICIPANT_FIELDS = ["player_id", "score"] as const

const EMPTY_VALUES: ParticipantFormInput = { player_id: "", score: "0" }

type PlayerPickerProps = {
  control: Control<ParticipantFormInput, unknown, ParticipantFormOutput>
  participantIds: ReadonlySet<number>
}

function PlayerPicker({ control, participantIds }: PlayerPickerProps) {
  const [search, setSearch] = useState("")
  const debouncedSearch = useDebouncedValue(search.trim())
  const players = usePlayerSearch(debouncedSearch)
  const playerOptions = (players.data?.results ?? [])
    .filter((player) => !participantIds.has(player.id))
    .map((player) => ({
      value: String(player.id),
      label: `${player.number} - ${player.name}`,
    }))

  return (
    <>
      <Field>
        <FieldLabel htmlFor="participant-search">Buscar jogador</FieldLabel>
        <Input
          id="participant-search"
          type="search"
          value={search}
          placeholder="Digite parte do nome"
          autoFocus
          onChange={(event) => setSearch(event.target.value)}
        />
        <FieldDescription>
          {players.isFetching
            ? "Buscando..."
            : `${playerOptions.length} jogador(es) disponível(is)`}
        </FieldDescription>
      </Field>
      <FormSelectField
        control={control}
        name="player_id"
        label="Jogador"
        id="participant-player"
        options={playerOptions}
        placeholder={
          playerOptions.length === 0 ? "Nenhum jogador encontrado" : "Selecione"
        }
      />
    </>
  )
}

type AddParticipantDialogProps = {
  eventId: number
  open: boolean
  participantIds: ReadonlySet<number>
  onOpenChange: (open: boolean) => void
}

export function AddParticipantDialog({
  eventId,
  open,
  participantIds,
  onOpenChange,
}: AddParticipantDialogProps) {
  const addParticipant = useAddParticipant(eventId)
  const form = useForm<ParticipantFormInput, unknown, ParticipantFormOutput>({
    resolver: zodResolver(participantSchema),
    defaultValues: EMPTY_VALUES,
  })

  useEffect(() => {
    if (open) {
      form.reset(EMPTY_VALUES)
    }
  }, [open, form])

  const onSubmit = form.handleSubmit(async (values) => {
    try {
      await addParticipant.mutateAsync(values)
      toast.success("Participante adicionado")
      onOpenChange(false)
    } catch (error) {
      applyApiErrors(error, PARTICIPANT_FIELDS, form.setError)
    }
  })

  return (
    <FormDialog
      open={open}
      title="Adicionar participante"
      description="Inscreva um jogador neste evento."
      pending={addParticipant.isPending}
      rootError={form.formState.errors.root?.message}
      submitLabel="Adicionar"
      onSubmit={onSubmit}
      onOpenChange={onOpenChange}
    >
      <PlayerPicker control={form.control} participantIds={participantIds} />
      <FormTextField
        control={form.control}
        name="score"
        label="Pontuação inicial"
        id="participant-score"
        inputMode="numeric"
      />
    </FormDialog>
  )
}
