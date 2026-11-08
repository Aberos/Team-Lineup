import { Pencil, Plus, Trash2 } from "lucide-react"
import { useState } from "react"
import { toast } from "sonner"

import { ConfirmDialog } from "@/components/common/ConfirmDialog"
import { EmptyState } from "@/components/common/EmptyState"
import { ErrorAlert } from "@/components/common/ErrorAlert"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Skeleton } from "@/components/ui/skeleton"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import { useConfirmState } from "@/lib/use-confirm-state"

import { useDeleteMatch, useMatches, useTeams } from "./hooks"
import { MatchFormDialog } from "./MatchFormDialog"
import { MATCH_STATUS, MATCH_STATUS_LABELS, type Match } from "./types"

const MIN_TEAMS_FOR_MATCH = 2

type MatchesTabProps = {
  eventId: number
}

export function MatchesTab({ eventId }: MatchesTabProps) {
  const matches = useMatches(eventId)
  const teams = useTeams(eventId)
  const deleteMatch = useDeleteMatch(eventId)
  const confirm = useConfirmState<Match>()
  const [dialogOpen, setDialogOpen] = useState(false)
  const [editingMatch, setEditingMatch] = useState<Match | null>(null)
  const teamList = teams.data ?? []
  const canCreateMatch = teamList.length >= MIN_TEAMS_FOR_MATCH

  const openDialog = (match: Match | null) => {
    setEditingMatch(match)
    setDialogOpen(true)
  }

  const handleDelete = () => {
    const match = confirm.target
    if (match === null) {
      return
    }
    deleteMatch.mutate(match.id, {
      onSuccess: () => toast.success("Partida excluída"),
      onError: () => toast.error("Não foi possível excluir a partida."),
      onSettled: confirm.close,
    })
  }

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-center justify-end gap-2">
        {teams.isSuccess && !canCreateMatch && (
          <p className="text-sm text-muted-foreground">
            Crie ao menos dois times para cadastrar partidas.
          </p>
        )}
        <Button onClick={() => openDialog(null)} disabled={!canCreateMatch}>
          <Plus />
          Nova partida
        </Button>
      </div>

      {matches.isPending && <Skeleton className="h-32 w-full" />}

      {matches.isError && (
        <ErrorAlert message="Não foi possível carregar as partidas." />
      )}

      {matches.isSuccess && matches.data.length === 0 && (
        <EmptyState message="Nenhuma partida cadastrada." />
      )}

      {matches.isSuccess && matches.data.length > 0 && (
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Partida</TableHead>
              <TableHead className="w-24 text-center">Placar</TableHead>
              <TableHead className="hidden sm:table-cell">Situação</TableHead>
              <TableHead className="w-24 text-right">Ações</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {matches.data.map((match) => {
              const title = `${match.team_home.team_name} x ${match.team_away.team_name}`
              return (
                <TableRow key={match.id}>
                  <TableCell className="font-medium">{title}</TableCell>
                  <TableCell className="text-center tabular-nums">
                    {match.score_team_home} x {match.score_team_away}
                  </TableCell>
                  <TableCell className="hidden sm:table-cell">
                    <Badge
                      variant={
                        match.status === MATCH_STATUS.COMPLETED
                          ? "secondary"
                          : "outline"
                      }
                    >
                      {MATCH_STATUS_LABELS[match.status]}
                    </Badge>
                  </TableCell>
                  <TableCell className="text-right">
                    <Button
                      variant="ghost"
                      size="icon"
                      aria-label={`Editar ${title}`}
                      onClick={() => openDialog(match)}
                    >
                      <Pencil />
                    </Button>
                    <Button
                      variant="ghost"
                      size="icon"
                      aria-label={`Excluir ${title}`}
                      onClick={() => confirm.ask(match)}
                    >
                      <Trash2 />
                    </Button>
                  </TableCell>
                </TableRow>
              )
            })}
          </TableBody>
        </Table>
      )}

      <MatchFormDialog
        eventId={eventId}
        open={dialogOpen}
        match={editingMatch}
        teams={teamList}
        onOpenChange={setDialogOpen}
      />
      <ConfirmDialog
        open={confirm.open}
        title="Excluir partida?"
        description="A partida e o placar serão removidos."
        pending={deleteMatch.isPending}
        onConfirm={handleDelete}
        onOpenChange={confirm.onOpenChange}
      />
    </div>
  )
}
