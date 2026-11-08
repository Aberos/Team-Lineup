import { zodResolver } from "@hookform/resolvers/zod"
import { useEffect } from "react"
import { useForm } from "react-hook-form"
import { toast } from "sonner"

import { FormDialog } from "@/components/common/FormDialog"
import { FormTextField } from "@/components/common/FormTextField"
import { applyApiErrors } from "@/lib/form-errors"

import { useUpdateScore } from "./hooks"
import {
  scoreSchema,
  type ScoreFormInput,
  type ScoreFormOutput,
} from "./schemas"
import type { Participant } from "./types"

const SCORE_FIELDS = ["score"] as const

type ScoreDialogProps = {
  eventId: number
  participant: Participant | null
  onOpenChange: (open: boolean) => void
}

export function ScoreDialog({
  eventId,
  participant,
  onOpenChange,
}: ScoreDialogProps) {
  const updateScore = useUpdateScore(eventId)
  const form = useForm<ScoreFormInput, unknown, ScoreFormOutput>({
    resolver: zodResolver(scoreSchema),
    defaultValues: { score: "0" },
  })

  useEffect(() => {
    if (participant !== null) {
      form.reset({ score: String(participant.score) })
    }
  }, [participant, form])

  const onSubmit = form.handleSubmit(async ({ score }) => {
    if (participant === null) {
      return
    }
    try {
      await updateScore.mutateAsync({ playerId: participant.player.id, score })
      toast.success("Pontuação atualizada")
      onOpenChange(false)
    } catch (error) {
      applyApiErrors(error, SCORE_FIELDS, form.setError)
    }
  })

  return (
    <FormDialog
      open={participant !== null}
      title="Editar pontuação"
      description={participant?.player.name ?? ""}
      pending={updateScore.isPending}
      rootError={form.formState.errors.root?.message}
      onSubmit={onSubmit}
      onOpenChange={onOpenChange}
    >
      <FormTextField
        control={form.control}
        name="score"
        label="Pontuação"
        id="participant-new-score"
        inputMode="numeric"
        autoFocus
      />
    </FormDialog>
  )
}
