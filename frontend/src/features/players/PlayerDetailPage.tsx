import { ArrowLeft, Pencil, Trash2 } from "lucide-react"
import { useState } from "react"
import { Link, useNavigate } from "react-router"
import { toast } from "sonner"

import { ConfirmDialog } from "@/components/common/ConfirmDialog"
import { EmptyState } from "@/components/common/EmptyState"
import { ErrorAlert } from "@/components/common/ErrorAlert"
import { PageHeader } from "@/components/common/PageHeader"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import { Skeleton } from "@/components/ui/skeleton"
import { isNotFound } from "@/lib/api-client"
import { formatDate } from "@/lib/format"
import { useIdParam } from "@/lib/use-id-param"

import { useDeletePlayer, usePlayer } from "./hooks"
import { PlayerAttributesCard } from "./PlayerAttributesCard"
import { PlayerFormDialog } from "./PlayerFormDialog"
import { PlayerRolesCard } from "./PlayerRolesCard"

type PlayerDetailContentProps = {
  playerId: number
}

function PlayerDetailContent({ playerId }: PlayerDetailContentProps) {
  const navigate = useNavigate()
  const player = usePlayer(playerId)
  const deletePlayer = useDeletePlayer()
  const [editOpen, setEditOpen] = useState(false)
  const [confirmOpen, setConfirmOpen] = useState(false)

  if (player.isPending) {
    return <Skeleton className="h-60 w-full" />
  }

  if (player.isError) {
    return isNotFound(player.error) ? (
      <EmptyState message="Jogador não encontrado." />
    ) : (
      <ErrorAlert message="Não foi possível carregar o jogador." />
    )
  }

  const handleDelete = () => {
    deletePlayer.mutate(playerId, {
      onSuccess: () => {
        toast.success("Jogador excluído")
        navigate("/players", { replace: true })
      },
      onError: () => toast.error("Não foi possível excluir o jogador."),
    })
  }

  const details = [
    { label: "Número", value: String(player.data.number) },
    { label: "Nascimento", value: formatDate(player.data.birthday) },
    { label: "Telefone", value: player.data.phone },
    { label: "E-mail", value: player.data.email },
  ]

  return (
    <>
      <PageHeader
        title={player.data.name}
        actions={
          <>
            <Button variant="outline" onClick={() => setEditOpen(true)}>
              <Pencil />
              Editar
            </Button>
            <Button variant="destructive" onClick={() => setConfirmOpen(true)}>
              <Trash2 />
              Excluir
            </Button>
          </>
        }
      />
      <Card>
        <CardContent>
          <dl className="grid gap-4 sm:grid-cols-2">
            {details.map((detail) => (
              <div key={detail.label}>
                <dt className="text-sm text-muted-foreground">
                  {detail.label}
                </dt>
                <dd className="font-medium break-all">{detail.value}</dd>
              </div>
            ))}
          </dl>
        </CardContent>
      </Card>
      <div className="grid gap-4 lg:grid-cols-2">
        <PlayerAttributesCard playerId={playerId} />
        <PlayerRolesCard playerId={playerId} />
      </div>
      <PlayerFormDialog
        open={editOpen}
        player={player.data}
        onOpenChange={setEditOpen}
      />
      <ConfirmDialog
        open={confirmOpen}
        title="Excluir jogador?"
        description={`${player.data.name} será removido de todos os eventos e times.`}
        pending={deletePlayer.isPending}
        onConfirm={handleDelete}
        onOpenChange={setConfirmOpen}
      />
    </>
  )
}

export function PlayerDetailPage() {
  const playerId = useIdParam("playerId")

  return (
    <section className="space-y-4">
      <Button variant="ghost" size="sm" asChild>
        <Link to="/players">
          <ArrowLeft />
          Jogadores
        </Link>
      </Button>
      {playerId === null ? (
        <EmptyState message="Jogador não encontrado." />
      ) : (
        <PlayerDetailContent playerId={playerId} />
      )}
    </section>
  )
}
