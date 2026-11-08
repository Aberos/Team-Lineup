import { Plus } from "lucide-react"
import { useState } from "react"
import { Link } from "react-router"

import { EmptyState } from "@/components/common/EmptyState"
import { ErrorAlert } from "@/components/common/ErrorAlert"
import { PageHeader } from "@/components/common/PageHeader"
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

import { usePlayers } from "./hooks"
import { PlayerFormDialog } from "./PlayerFormDialog"

export function PlayersPage() {
  const players = usePlayers()
  const [dialogOpen, setDialogOpen] = useState(false)

  return (
    <section className="space-y-4">
      <PageHeader
        title="Jogadores"
        actions={
          <Button onClick={() => setDialogOpen(true)}>
            <Plus />
            Novo jogador
          </Button>
        }
      />

      {players.isPending && <Skeleton className="h-40 w-full" />}

      {players.isError && (
        <ErrorAlert message="Não foi possível carregar os jogadores." />
      )}

      {players.isSuccess && players.data.length === 0 && (
        <EmptyState message="Nenhum jogador cadastrado." />
      )}

      {players.isSuccess && players.data.length > 0 && (
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead className="w-20">Número</TableHead>
              <TableHead>Nome</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {players.data.map((player) => (
              <TableRow key={player.id}>
                <TableCell className="font-medium">{player.number}</TableCell>
                <TableCell>
                  <Link
                    to={`/players/${player.id}`}
                    className="underline-offset-4 hover:underline"
                  >
                    {player.name}
                  </Link>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      )}

      <PlayerFormDialog
        open={dialogOpen}
        player={null}
        onOpenChange={setDialogOpen}
      />
    </section>
  )
}
