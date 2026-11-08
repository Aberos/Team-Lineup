import { Plus } from "lucide-react"
import { useState } from "react"
import { Link, useNavigate } from "react-router"

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
import { formatDate } from "@/lib/format"

import { EventFormDialog } from "./EventFormDialog"
import { useEvents } from "./hooks"

export function EventsPage() {
  const events = useEvents()
  const navigate = useNavigate()
  const [dialogOpen, setDialogOpen] = useState(false)

  return (
    <section className="space-y-4">
      <PageHeader
        title="Eventos"
        actions={
          <Button onClick={() => setDialogOpen(true)}>
            <Plus />
            Novo evento
          </Button>
        }
      />

      {events.isPending && <Skeleton className="h-40 w-full" />}

      {events.isError && (
        <ErrorAlert message="Não foi possível carregar os eventos." />
      )}

      {events.isSuccess && events.data.length === 0 && (
        <EmptyState message="Nenhum evento cadastrado." />
      )}

      {events.isSuccess && events.data.length > 0 && (
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead className="w-28">Data</TableHead>
              <TableHead>Evento</TableHead>
              <TableHead className="hidden sm:table-cell">Local</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {events.data.map((event) => (
              <TableRow key={event.id}>
                <TableCell>{formatDate(event.date)}</TableCell>
                <TableCell>
                  <Link
                    to={`/events/${event.id}`}
                    className="font-medium underline-offset-4 hover:underline"
                  >
                    {event.name}
                  </Link>
                </TableCell>
                <TableCell className="hidden sm:table-cell">
                  {event.location}
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      )}

      <EventFormDialog
        open={dialogOpen}
        event={null}
        onOpenChange={setDialogOpen}
        onCreated={(event) => navigate(`/events/${event.id}`)}
      />
    </section>
  )
}
