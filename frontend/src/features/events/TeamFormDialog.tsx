import { zodResolver } from "@hookform/resolvers/zod"
import { useEffect } from "react"
import { useForm } from "react-hook-form"
import { toast } from "sonner"

import { FormDialog } from "@/components/common/FormDialog"
import { FormTextField } from "@/components/common/FormTextField"
import { applyApiErrors } from "@/lib/form-errors"

import { useSaveTeam } from "./hooks"
import { teamSchema, type TeamFormValues } from "./schemas"
import type { Team } from "./types"

const TEAM_FIELDS = ["team_name"] as const

type TeamFormDialogProps = {
  eventId: number
  open: boolean
  team: Team | null
  onOpenChange: (open: boolean) => void
}

export function TeamFormDialog({
  eventId,
  open,
  team,
  onOpenChange,
}: TeamFormDialogProps) {
  const saveTeam = useSaveTeam(eventId)
  const form = useForm<TeamFormValues>({
    resolver: zodResolver(teamSchema),
    defaultValues: { team_name: "" },
  })

  useEffect(() => {
    if (open) {
      form.reset({ team_name: team?.team_name ?? "" })
    }
  }, [open, team, form])

  const onSubmit = form.handleSubmit(async ({ team_name: teamName }) => {
    try {
      await saveTeam.mutateAsync({ teamId: team?.id ?? null, teamName })
      toast.success(team === null ? "Time criado" : "Time renomeado")
      onOpenChange(false)
    } catch (error) {
      applyApiErrors(error, TEAM_FIELDS, form.setError)
    }
  })

  return (
    <FormDialog
      open={open}
      title={team === null ? "Novo time" : "Renomear time"}
      description="O nome precisa ser único dentro do evento."
      pending={saveTeam.isPending}
      rootError={form.formState.errors.root?.message}
      onSubmit={onSubmit}
      onOpenChange={onOpenChange}
    >
      <FormTextField
        control={form.control}
        name="team_name"
        label="Nome do time"
        id="team-name"
        autoFocus
      />
    </FormDialog>
  )
}
