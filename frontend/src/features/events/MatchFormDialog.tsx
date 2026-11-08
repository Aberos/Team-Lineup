import { zodResolver } from "@hookform/resolvers/zod"
import { useEffect } from "react"
import { useForm } from "react-hook-form"
import { toast } from "sonner"

import { FormDialog } from "@/components/common/FormDialog"
import { FormSelectField } from "@/components/common/FormSelectField"
import { FormTextField } from "@/components/common/FormTextField"
import { applyApiErrors } from "@/lib/form-errors"

import { useSaveMatch } from "./hooks"
import {
  matchSchema,
  type MatchFormInput,
  type MatchFormOutput,
} from "./schemas"
import {
  MATCH_STATUS,
  MATCH_STATUS_LABELS,
  type Match,
  type Team,
} from "./types"

const MATCH_FIELDS = [
  "team_home_id",
  "team_away_id",
  "score_team_home",
  "score_team_away",
  "status",
] as const

const STATUS_OPTIONS = (
  Object.entries(MATCH_STATUS_LABELS) as Array<[string, string]>
).map(([value, label]) => ({ value, label }))

function toFormValues(match: Match | null): MatchFormInput {
  if (match === null) {
    return {
      team_home_id: "",
      team_away_id: "",
      score_team_home: "0",
      score_team_away: "0",
      status: String(MATCH_STATUS.SCHEDULED),
    }
  }
  return {
    team_home_id: String(match.team_home.id),
    team_away_id: String(match.team_away.id),
    score_team_home: String(match.score_team_home),
    score_team_away: String(match.score_team_away),
    status: String(match.status),
  }
}

type MatchFormDialogProps = {
  eventId: number
  open: boolean
  match: Match | null
  teams: ReadonlyArray<Team>
  onOpenChange: (open: boolean) => void
}

export function MatchFormDialog({
  eventId,
  open,
  match,
  teams,
  onOpenChange,
}: MatchFormDialogProps) {
  const saveMatch = useSaveMatch(eventId)
  const form = useForm<MatchFormInput, unknown, MatchFormOutput>({
    resolver: zodResolver(matchSchema),
    defaultValues: toFormValues(null),
  })
  const teamOptions = teams.map((team) => ({
    value: String(team.id),
    label: team.team_name,
  }))

  useEffect(() => {
    if (open) {
      form.reset(toFormValues(match))
    }
  }, [open, match, form])

  const onSubmit = form.handleSubmit(async (payload) => {
    try {
      await saveMatch.mutateAsync({ matchId: match?.id ?? null, payload })
      toast.success(match === null ? "Partida criada" : "Partida atualizada")
      onOpenChange(false)
    } catch (error) {
      applyApiErrors(error, MATCH_FIELDS, form.setError)
    }
  })

  return (
    <FormDialog
      open={open}
      title={match === null ? "Nova partida" : "Editar partida"}
      description="Times, placar e situação da partida."
      pending={saveMatch.isPending}
      rootError={form.formState.errors.root?.message}
      onSubmit={onSubmit}
      onOpenChange={onOpenChange}
    >
      <div className="grid gap-4 sm:grid-cols-2">
        <FormSelectField
          control={form.control}
          name="team_home_id"
          label="Mandante"
          id="match-home"
          options={teamOptions}
          placeholder="Selecione"
        />
        <FormSelectField
          control={form.control}
          name="team_away_id"
          label="Visitante"
          id="match-away"
          options={teamOptions}
          placeholder="Selecione"
        />
        <FormTextField
          control={form.control}
          name="score_team_home"
          label="Gols do mandante"
          id="match-score-home"
          inputMode="numeric"
        />
        <FormTextField
          control={form.control}
          name="score_team_away"
          label="Gols do visitante"
          id="match-score-away"
          inputMode="numeric"
        />
      </div>
      <FormSelectField
        control={form.control}
        name="status"
        label="Situação"
        id="match-status"
        options={STATUS_OPTIONS}
      />
    </FormDialog>
  )
}
