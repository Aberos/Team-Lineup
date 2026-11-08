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

import { useDeleteRole, useRoles } from "./hooks"
import { RoleFormDialog } from "./RoleFormDialog"
import type { Role } from "./types"

export function RolesPage() {
  const roles = useRoles()
  const deleteRole = useDeleteRole()
  const confirm = useConfirmState<Role>()
  const [dialogOpen, setDialogOpen] = useState(false)
  const [editingRole, setEditingRole] = useState<Role | null>(null)

  const openDialog = (role: Role | null) => {
    setEditingRole(role)
    setDialogOpen(true)
  }

  const handleDelete = () => {
    const role = confirm.target
    if (role === null) {
      return
    }
    deleteRole.mutate(role.id, {
      onSuccess: () => toast.success(`Função "${role.name}" excluída`),
      onError: () => toast.error("Não foi possível excluir a função."),
      onSettled: confirm.close,
    })
  }

  return (
    <section className="space-y-4">
      <PageHeader
        title="Funções"
        actions={
          <Button onClick={() => openDialog(null)}>
            <Plus />
            Nova função
          </Button>
        }
      />

      {roles.isPending && <Skeleton className="h-40 w-full" />}

      {roles.isError && (
        <ErrorAlert message="Não foi possível carregar as funções." />
      )}

      {roles.isSuccess && roles.data.length === 0 && (
        <EmptyState message="Nenhuma função cadastrada." />
      )}

      {roles.isSuccess && roles.data.length > 0 && (
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Função</TableHead>
              <TableHead className="w-24 text-right">Ações</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {roles.data.map((role) => (
              <TableRow key={role.id}>
                <TableCell>{role.name}</TableCell>
                <TableCell className="text-right">
                  <Button
                    variant="ghost"
                    size="icon"
                    aria-label={`Editar ${role.name}`}
                    onClick={() => openDialog(role)}
                  >
                    <Pencil />
                  </Button>
                  <Button
                    variant="ghost"
                    size="icon"
                    aria-label={`Excluir ${role.name}`}
                    onClick={() => confirm.ask(role)}
                  >
                    <Trash2 />
                  </Button>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      )}

      <RoleFormDialog
        open={dialogOpen}
        role={editingRole}
        onOpenChange={setDialogOpen}
      />
      <ConfirmDialog
        open={confirm.open}
        title="Excluir função?"
        description={`A função "${confirm.target?.name ?? ""}" será removida de todos os jogadores.`}
        pending={deleteRole.isPending}
        onConfirm={handleDelete}
        onOpenChange={confirm.onOpenChange}
      />
    </section>
  )
}
