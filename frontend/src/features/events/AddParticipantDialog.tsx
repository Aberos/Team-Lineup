import { zodResolver } from "@hookform/resolvers/zod"
import { useEffect } from "react"
import { useForm } from "react-hook-form"
import { toast } from "sonner"

import type { SelectOption } from "@/components/common/FormSelectField"
import { FormSelectField } from "@/components/common/FormSelectField"
import { FormDialog } from "@/components/common/FormDialog"
import { FormTextField } from "@/components/common/FormTextField"
import { applyApiErrors } from "@/lib/form-errors"

import { useAddParticipant } from "./hooks"
import {
  participantSchema,
  type ParticipantFormInput,
  type ParticipantFormOutput,
} from "./schemas"

const PARTICIPANT_FIELDS = ["player_id", "score"] as const

const EMPTY_VALUES: ParticipantFormInput = { player_id: "", score: "0" }

type AddParticipantDialogProps = {
  eventId: number
  open: boolean
  playerOptions: ReadonlyArray<SelectOption>
  onOpenChange: (open: boolean) => void
}

export function AddParticipantDialog({
  eventId,
  open,
  playerOptions,
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
      <FormSelectField
        control={form.control}
        name="player_id"
        label="Jogador"
        id="participant-player"
        options={playerOptions}
        placeholder="Selecione"
      />
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
