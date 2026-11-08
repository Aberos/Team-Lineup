import { Pencil, Plus, Trash2 } from "lucide-react"
import { useState } from "react"
import { toast } from "sonner"

import { ConfirmDialog } from "@/components/common/ConfirmDialog"
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
import { useConfirmState } from "@/lib/use-confirm-state"

import { AttributeFormDialog } from "./AttributeFormDialog"
import { useAttributes, useDeleteAttribute } from "./hooks"
import type { Attribute } from "./types"

export function AttributesPage() {
  const attributes = useAttributes()
  const deleteAttribute = useDeleteAttribute()
  const confirm = useConfirmState<Attribute>()
  const [dialogOpen, setDialogOpen] = useState(false)
  const [editing, setEditing] = useState<Attribute | null>(null)

  const openDialog = (attribute: Attribute | null) => {
    setEditing(attribute)
    setDialogOpen(true)
  }

  const handleDelete = () => {
    const attribute = confirm.target
    if (attribute === null) {
      return
    }
    deleteAttribute.mutate(attribute.id, {
      onSuccess: () => toast.success(`Atributo "${attribute.name}" excluído`),
      onError: () => toast.error("Não foi possível excluir o atributo."),
      onSettled: confirm.close,
    })
  }

  return (
    <section className="space-y-4">
      <PageHeader
        title="Atributos"
        description="Habilidades avaliadas em cada jogador, com nota de 0 a 100."
        actions={
          <Button onClick={() => openDialog(null)}>
            <Plus />
            Novo atributo
          </Button>
        }
      />

      {attributes.isPending && <Skeleton className="h-40 w-full" />}

      {attributes.isError && (
        <ErrorAlert message="Não foi possível carregar os atributos." />
      )}

      {attributes.isSuccess && attributes.data.length === 0 && (
        <EmptyState message="Nenhum atributo cadastrado." />
      )}

      {attributes.isSuccess && attributes.data.length > 0 && (
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Atributo</TableHead>
              <TableHead className="w-24 text-right">Ações</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {attributes.data.map((attribute) => (
              <TableRow key={attribute.id}>
                <TableCell>{attribute.name}</TableCell>
                <TableCell className="text-right">
                  <Button
                    variant="ghost"
                    size="icon"
                    aria-label={`Editar ${attribute.name}`}
                    onClick={() => openDialog(attribute)}
                  >
                    <Pencil />
                  </Button>
                  <Button
                    variant="ghost"
                    size="icon"
                    aria-label={`Excluir ${attribute.name}`}
                    onClick={() => confirm.ask(attribute)}
                  >
                    <Trash2 />
                  </Button>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      )}

      <AttributeFormDialog
        open={dialogOpen}
        attribute={editing}
        onOpenChange={setDialogOpen}
      />
      <ConfirmDialog
        open={confirm.open}
        title="Excluir atributo?"
        description={`As notas de "${confirm.target?.name ?? ""}" serão removidas de todos os jogadores.`}
        pending={deleteAttribute.isPending}
        onConfirm={handleDelete}
        onOpenChange={confirm.onOpenChange}
      />
    </section>
  )
}
