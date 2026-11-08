import { zodResolver } from "@hookform/resolvers/zod"
import { useEffect } from "react"
import { useForm } from "react-hook-form"
import { toast } from "sonner"

import { FormDialog } from "@/components/common/FormDialog"
import { FormTextField } from "@/components/common/FormTextField"
import { applyApiErrors } from "@/lib/form-errors"

import { useCreateEvent, useUpdateEvent } from "./hooks"
import { eventSchema, type EventFormValues } from "./schemas"
import type { Event } from "./types"

const EVENT_FIELDS = ["name", "date", "location"] as const

const EMPTY_VALUES: EventFormValues = { name: "", date: "", location: "" }

type EventFormDialogProps = {
  open: boolean
  event: Event | null
  onOpenChange: (open: boolean) => void
  onCreated?: (event: Event) => void
}

export function EventFormDialog({
  open,
  event,
  onOpenChange,
  onCreated,
}: EventFormDialogProps) {
  const createEvent = useCreateEvent()
  const updateEvent = useUpdateEvent()
  const form = useForm<EventFormValues>({
    resolver: zodResolver(eventSchema),
    defaultValues: EMPTY_VALUES,
  })

  useEffect(() => {
    if (open) {
      form.reset(
        event === null
          ? EMPTY_VALUES
          : { name: event.name, date: event.date, location: event.location },
      )
    }
  }, [open, event, form])

  const onSubmit = form.handleSubmit(async (values) => {
    try {
      if (event === null) {
        const created = await createEvent.mutateAsync(values)
        toast.success("Evento criado")
        onCreated?.(created)
      } else {
        await updateEvent.mutateAsync({ id: event.id, payload: values })
        toast.success("Evento atualizado")
      }
      onOpenChange(false)
    } catch (error) {
      applyApiErrors(error, EVENT_FIELDS, form.setError)
    }
  })

  return (
    <FormDialog
      open={open}
      title={event === null ? "Novo evento" : "Editar evento"}
      description="Nome, data e local do evento."
      pending={createEvent.isPending || updateEvent.isPending}
      rootError={form.formState.errors.root?.message}
      onSubmit={onSubmit}
      onOpenChange={onOpenChange}
    >
      <FormTextField
        control={form.control}
        name="name"
        label="Nome"
        id="event-name"
        autoFocus
      />
      <FormTextField
        control={form.control}
        name="date"
        label="Data"
        id="event-date"
        type="date"
      />
      <FormTextField
        control={form.control}
        name="location"
        label="Local"
        id="event-location"
      />
    </FormDialog>
  )
}
