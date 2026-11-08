import { ArrowLeft, CalendarDays, MapPin, Pencil, Trash2 } from "lucide-react"
import { useState } from "react"
import { Link, useNavigate } from "react-router"
import { toast } from "sonner"

import { ConfirmDialog } from "@/components/common/ConfirmDialog"
import { EmptyState } from "@/components/common/EmptyState"
import { ErrorAlert } from "@/components/common/ErrorAlert"
import { PageHeader } from "@/components/common/PageHeader"
import { Button } from "@/components/ui/button"
import { Skeleton } from "@/components/ui/skeleton"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { isNotFound } from "@/lib/api-client"
import { formatDate } from "@/lib/format"
import { useIdParam } from "@/lib/use-id-param"

import { EventFormDialog } from "./EventFormDialog"
import { useDeleteEvent, useEvent } from "./hooks"
import { MatchesTab } from "./MatchesTab"
import { ParticipantsTab } from "./ParticipantsTab"
import { TeamsTab } from "./TeamsTab"

type EventDetailContentProps = {
  eventId: number
}

function EventDetailContent({ eventId }: EventDetailContentProps) {
  const navigate = useNavigate()
  const event = useEvent(eventId)
  const deleteEvent = useDeleteEvent()
  const [editOpen, setEditOpen] = useState(false)
  const [confirmOpen, setConfirmOpen] = useState(false)

  if (event.isPending) {
    return <Skeleton className="h-60 w-full" />
  }

  if (event.isError) {
    return isNotFound(event.error) ? (
      <EmptyState message="Evento não encontrado." />
    ) : (
      <ErrorAlert message="Não foi possível carregar o evento." />
    )
  }

  const handleDelete = () => {
    deleteEvent.mutate(eventId, {
      onSuccess: () => {
        toast.success("Evento excluído")
        navigate("/events", { replace: true })
      },
      onError: () => toast.error("Não foi possível excluir o evento."),
    })
  }

  return (
    <>
      <PageHeader
        title={event.data.name}
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
      <div className="flex flex-wrap gap-4 text-sm text-muted-foreground">
        <span className="flex items-center gap-1">
          <CalendarDays className="size-4" />
          {formatDate(event.data.date)}
        </span>
        <span className="flex items-center gap-1">
          <MapPin className="size-4" />
          {event.data.location}
        </span>
      </div>
      <Tabs defaultValue="participants">
        <TabsList>
          <TabsTrigger value="participants">Participantes</TabsTrigger>
          <TabsTrigger value="teams">Times</TabsTrigger>
          <TabsTrigger value="matches">Partidas</TabsTrigger>
        </TabsList>
        <TabsContent value="participants" className="pt-2">
          <ParticipantsTab eventId={eventId} />
        </TabsContent>
        <TabsContent value="teams" className="pt-2">
          <TeamsTab eventId={eventId} />
        </TabsContent>
        <TabsContent value="matches" className="pt-2">
          <MatchesTab eventId={eventId} />
        </TabsContent>
      </Tabs>
      <EventFormDialog
        open={editOpen}
        event={event.data}
        onOpenChange={setEditOpen}
      />
      <ConfirmDialog
        open={confirmOpen}
        title="Excluir evento?"
        description="Participantes, times e partidas deste evento também serão excluídos."
        pending={deleteEvent.isPending}
        onConfirm={handleDelete}
        onOpenChange={setConfirmOpen}
      />
    </>
  )
}

export function EventDetailPage() {
  const eventId = useIdParam("eventId")

  return (
    <section className="space-y-4">
      <Button variant="ghost" size="sm" asChild>
        <Link to="/events">
          <ArrowLeft />
          Eventos
        </Link>
      </Button>
      {eventId === null ? (
        <EmptyState message="Evento não encontrado." />
      ) : (
        <EventDetailContent eventId={eventId} />
      )}
    </section>
  )
}
