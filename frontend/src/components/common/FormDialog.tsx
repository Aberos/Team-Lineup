import type { FormEventHandler, ReactNode } from "react"

import { Button } from "@/components/ui/button"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import { FieldError, FieldGroup } from "@/components/ui/field"

type FormDialogProps = {
  open: boolean
  title: string
  description: string
  pending: boolean
  rootError?: string
  submitLabel?: string
  children: ReactNode
  onSubmit: FormEventHandler<HTMLFormElement>
  onOpenChange: (open: boolean) => void
}

export function FormDialog({
  open,
  title,
  description,
  pending,
  rootError,
  submitLabel = "Salvar",
  children,
  onSubmit,
  onOpenChange,
}: FormDialogProps) {
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>{title}</DialogTitle>
          <DialogDescription>{description}</DialogDescription>
        </DialogHeader>
        <form onSubmit={onSubmit} noValidate>
          <FieldGroup>
            {children}
            {rootError && <FieldError>{rootError}</FieldError>}
            <DialogFooter>
              <Button
                type="button"
                variant="outline"
                onClick={() => onOpenChange(false)}
              >
                Cancelar
              </Button>
              <Button type="submit" disabled={pending}>
                {submitLabel}
              </Button>
            </DialogFooter>
          </FieldGroup>
        </form>
      </DialogContent>
    </Dialog>
  )
}
