import { Pencil, Plus, Trash2 } from "lucide-react"
import { useState } from "react"
import { toast } from "sonner"

import { ConfirmDialog } from "@/components/common/ConfirmDialog"
import { EmptyState } from "@/components/common/EmptyState"
import { ErrorAlert } from "@/components/common/ErrorAlert"
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
import { usePlayers } from "@/features/players/hooks"
import { useConfirmState } from "@/lib/use-confirm-state"

import { AddParticipantDialog } from "./AddParticipantDialog"
import { useParticipants, useRemoveParticipant } from "./hooks"
import { ScoreDialog } from "./ScoreDialog"
import type { Participant } from "./types"

type ParticipantsTabProps = {
  eventId: number
}

export function ParticipantsTab({ eventId }: ParticipantsTabProps) {
  const participants = useParticipants(eventId)
  const players = usePlayers()
  const removeParticipant = useRemoveParticipant(eventId)
  const confirm = useConfirmState<Participant>()
  const [addOpen, setAddOpen] = useState(false)
  const [editing, setEditing] = useState<Participant | null>(null)

  const participantIds = new Set(
    participants.data?.map((participant) => participant.player.id),
  )
  const playerOptions = (players.data ?? [])
    .filter((player) => !participantIds.has(player.id))
    .map((player) => ({
      value: String(player.id),
      label: `${player.number} - ${player.name}`,
    }))

  const handleRemove = () => {
    const participant = confirm.target
    if (participant === null) {
      return
    }
    removeParticipant.mutate(participant.player.id, {
      onSuccess: () => toast.success("Participante removido"),
      onError: () => toast.error("Não foi possível remover o participante."),
      onSettled: confirm.close,
    })
  }

  return (
    <div className="space-y-4">
      <div className="flex justify-end">
        <Button
          onClick={() => setAddOpen(true)}
          disabled={playerOptions.length === 0}
        >
          <Plus />
          Adicionar participante
        </Button>
      </div>

      {participants.isPending && <Skeleton className="h-32 w-full" />}

      {participants.isError && (
        <ErrorAlert message="Não foi possível carregar os participantes." />
      )}

      {participants.isSuccess && participants.data.length === 0 && (
        <EmptyState message="Nenhum participante inscrito." />
      )}

      {participants.isSuccess && participants.data.length > 0 && (
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead className="w-16">Nº</TableHead>
              <TableHead>Jogador</TableHead>
              <TableHead className="w-24 text-right">Pontos</TableHead>
              <TableHead className="w-24 text-right">Ações</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {participants.data.map((participant) => (
              <TableRow key={participant.player.id}>
                <TableCell>{participant.player.number}</TableCell>
                <TableCell>{participant.player.name}</TableCell>
                <TableCell className="text-right font-medium">
                  {participant.score}
                </TableCell>
                <TableCell className="text-right">
                  <Button
                    variant="ghost"
                    size="icon"
                    aria-label={`Editar pontuação de ${participant.player.name}`}
                    onClick={() => setEditing(participant)}
                  >
                    <Pencil />
                  </Button>
                  <Button
                    variant="ghost"
                    size="icon"
                    aria-label={`Remover ${participant.player.name}`}
                    onClick={() => confirm.ask(participant)}
                  >
                    <Trash2 />
                  </Button>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      )}

      <AddParticipantDialog
        eventId={eventId}
        open={addOpen}
        playerOptions={playerOptions}
        onOpenChange={setAddOpen}
      />
      <ScoreDialog
        eventId={eventId}
        participant={editing}
        onOpenChange={(open) => {
          if (!open) {
            setEditing(null)
          }
        }}
      />
      <ConfirmDialog
        open={confirm.open}
        title="Remover participante?"
        description={`${confirm.target?.player.name ?? ""} também sairá dos times deste evento.`}
        confirmLabel="Remover"
        pending={removeParticipant.isPending}
        onConfirm={handleRemove}
        onOpenChange={confirm.onOpenChange}
      />
    </div>
  )
}
