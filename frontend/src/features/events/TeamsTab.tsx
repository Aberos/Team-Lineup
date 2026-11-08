import { Plus } from "lucide-react"
import { useState } from "react"
import { toast } from "sonner"

import { ConfirmDialog } from "@/components/common/ConfirmDialog"
import { EmptyState } from "@/components/common/EmptyState"
import { ErrorAlert } from "@/components/common/ErrorAlert"
import { Button } from "@/components/ui/button"
import { Skeleton } from "@/components/ui/skeleton"
import { useConfirmState } from "@/lib/use-confirm-state"

import { useDeleteTeam, useParticipants, useTeamMembers, useTeams } from "./hooks"
import { TeamCard } from "./TeamCard"
import { TeamFormDialog } from "./TeamFormDialog"
import type { Team } from "./types"

type TeamsTabProps = {
  eventId: number
}

export function TeamsTab({ eventId }: TeamsTabProps) {
  const teams = useTeams(eventId)
  const participants = useParticipants(eventId)
  const teamIds = teams.data?.map((team) => team.id) ?? []
  const members = useTeamMembers(eventId, teamIds)
  const deleteTeam = useDeleteTeam(eventId)
  const confirm = useConfirmState<Team>()
  const [dialogOpen, setDialogOpen] = useState(false)
  const [editingTeam, setEditingTeam] = useState<Team | null>(null)

  const assignedIds = new Set(
    [...members.membersByTeam.values()].flatMap((teamMembers) =>
      teamMembers.map((member) => member.player.id),
    ),
  )
  const availableOptions = (participants.data ?? [])
    .filter((participant) => !assignedIds.has(participant.player.id))
    .map((participant) => ({
      value: String(participant.player.id),
      label: `${participant.player.number} - ${participant.player.name}`,
    }))

  const openDialog = (team: Team | null) => {
    setEditingTeam(team)
    setDialogOpen(true)
  }

  const handleDelete = () => {
    const team = confirm.target
    if (team === null) {
      return
    }
    deleteTeam.mutate(team.id, {
      onSuccess: () => toast.success(`Time "${team.team_name}" excluído`),
      onError: () => toast.error("Não foi possível excluir o time."),
      onSettled: confirm.close,
    })
  }

  return (
    <div className="space-y-4">
      <div className="flex justify-end">
        <Button onClick={() => openDialog(null)}>
          <Plus />
          Novo time
        </Button>
      </div>

      {(teams.isPending || members.isPending) && (
        <Skeleton className="h-32 w-full" />
      )}

      {(teams.isError || members.isError) && (
        <ErrorAlert message="Não foi possível carregar os times." />
      )}

      {teams.isSuccess && teams.data.length === 0 && (
        <EmptyState message="Nenhum time criado." />
      )}

      {teams.isSuccess && !members.isPending && teams.data.length > 0 && (
        <div className="grid gap-4 md:grid-cols-2">
          {teams.data.map((team) => (
            <TeamCard
              key={team.id}
              eventId={eventId}
              team={team}
              members={members.membersByTeam.get(team.id) ?? []}
              availableOptions={availableOptions}
              onRename={openDialog}
              onDelete={confirm.ask}
            />
          ))}
        </div>
      )}

      <TeamFormDialog
        eventId={eventId}
        open={dialogOpen}
        team={editingTeam}
        onOpenChange={setDialogOpen}
      />
      <ConfirmDialog
        open={confirm.open}
        title="Excluir time?"
        description={`"${confirm.target?.team_name ?? ""}" e as partidas dele serão excluídos.`}
        pending={deleteTeam.isPending}
        onConfirm={handleDelete}
        onOpenChange={confirm.onOpenChange}
      />
    </div>
  )
}
