import { zodResolver } from "@hookform/resolvers/zod"
import { Pencil, Plus, Trash2, X } from "lucide-react"
import { useForm } from "react-hook-form"
import { toast } from "sonner"

import type { SelectOption } from "@/components/common/FormSelectField"
import { FormSelectField } from "@/components/common/FormSelectField"
import { Button } from "@/components/ui/button"
import {
  Card,
  CardAction,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { FieldError } from "@/components/ui/field"
import { applyApiErrors } from "@/lib/form-errors"

import { useAddMember, useRemoveMember } from "./hooks"
import {
  memberSchema,
  type MemberFormInput,
  type MemberFormOutput,
} from "./schemas"
import type { Team, TeamMember } from "./types"

const MEMBER_FIELDS = ["player_id"] as const

type TeamCardProps = {
  eventId: number
  team: Team
  members: ReadonlyArray<TeamMember>
  availableOptions: ReadonlyArray<SelectOption>
  onRename: (team: Team) => void
  onDelete: (team: Team) => void
}

export function TeamCard({
  eventId,
  team,
  members,
  availableOptions,
  onRename,
  onDelete,
}: TeamCardProps) {
  const addMember = useAddMember(eventId)
  const removeMember = useRemoveMember(eventId)
  const form = useForm<MemberFormInput, unknown, MemberFormOutput>({
    resolver: zodResolver(memberSchema),
    defaultValues: { player_id: "" },
  })

  const onSubmit = form.handleSubmit(async ({ player_id: playerId }) => {
    try {
      await addMember.mutateAsync({ teamId: team.id, playerId })
      form.reset({ player_id: "" })
      toast.success("Jogador adicionado ao time")
    } catch (error) {
      applyApiErrors(error, MEMBER_FIELDS, form.setError)
    }
  })

  const handleRemove = (member: TeamMember) => {
    removeMember.mutate(
      { teamId: team.id, playerId: member.player.id },
      {
        onSuccess: () => toast.success(`${member.player.name} saiu do time`),
        onError: () => toast.error("Não foi possível remover o jogador."),
      },
    )
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>{team.team_name}</CardTitle>
        <CardAction>
          <Button
            variant="ghost"
            size="icon"
            aria-label={`Renomear ${team.team_name}`}
            onClick={() => onRename(team)}
          >
            <Pencil />
          </Button>
          <Button
            variant="ghost"
            size="icon"
            aria-label={`Excluir ${team.team_name}`}
            onClick={() => onDelete(team)}
          >
            <Trash2 />
          </Button>
        </CardAction>
      </CardHeader>
      <CardContent className="space-y-4">
        {members.length === 0 ? (
          <p className="text-sm text-muted-foreground">Time sem jogadores.</p>
        ) : (
          <ul className="divide-y rounded-md border">
            {members.map((member) => (
              <li
                key={member.player.id}
                className="flex items-center justify-between gap-2 px-3 py-1.5 text-sm"
              >
                <span>
                  <span className="mr-2 text-muted-foreground">
                    {member.player.number}
                  </span>
                  {member.player.name}
                </span>
                <Button
                  variant="ghost"
                  size="icon"
                  aria-label={`Tirar ${member.player.name} do time`}
                  disabled={removeMember.isPending}
                  onClick={() => handleRemove(member)}
                >
                  <X />
                </Button>
              </li>
            ))}
          </ul>
        )}
        <form
          onSubmit={onSubmit}
          noValidate
          className="flex flex-col gap-2 sm:flex-row sm:items-end"
        >
          <div className="flex-1">
            <FormSelectField
              control={form.control}
              name="player_id"
              label="Adicionar jogador"
              id={`team-${team.id}-member`}
              options={availableOptions}
              placeholder={
                availableOptions.length === 0
                  ? "Nenhum participante livre"
                  : "Selecione"
              }
            />
          </div>
          <Button
            type="submit"
            variant="secondary"
            disabled={addMember.isPending || availableOptions.length === 0}
          >
            <Plus />
            Adicionar
          </Button>
        </form>
        {form.formState.errors.root && (
          <FieldError>{form.formState.errors.root.message}</FieldError>
        )}
      </CardContent>
    </Card>
  )
}
