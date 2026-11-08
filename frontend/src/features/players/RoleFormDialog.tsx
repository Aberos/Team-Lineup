import { zodResolver } from "@hookform/resolvers/zod"
import { useEffect } from "react"
import { useForm } from "react-hook-form"
import { toast } from "sonner"

import { FormDialog } from "@/components/common/FormDialog"
import { FormTextField } from "@/components/common/FormTextField"
import { applyApiErrors } from "@/lib/form-errors"

import { useCreateRole, useUpdateRole } from "./hooks"
import { roleSchema, type RoleValues } from "./schemas"
import type { Role } from "./types"

const ROLE_FIELDS = ["name"] as const

type RoleFormDialogProps = {
  open: boolean
  role: Role | null
  onOpenChange: (open: boolean) => void
}

export function RoleFormDialog({
  open,
  role,
  onOpenChange,
}: RoleFormDialogProps) {
  const createRole = useCreateRole()
  const updateRole = useUpdateRole()
  const form = useForm<RoleValues>({
    resolver: zodResolver(roleSchema),
    defaultValues: { name: "" },
  })

  useEffect(() => {
    if (open) {
      form.reset({ name: role?.name ?? "" })
    }
  }, [open, role, form])

  const onSubmit = form.handleSubmit(async (values) => {
    try {
      if (role === null) {
        await createRole.mutateAsync(values)
        toast.success("Função criada")
      } else {
        await updateRole.mutateAsync({ id: role.id, payload: values })
        toast.success("Função atualizada")
      }
      onOpenChange(false)
    } catch (error) {
      applyApiErrors(error, ROLE_FIELDS, form.setError)
    }
  })

  return (
    <FormDialog
      open={open}
      title={role === null ? "Nova função" : "Editar função"}
      description="Funções descrevem a posição de um jogador no time."
      pending={createRole.isPending || updateRole.isPending}
      rootError={form.formState.errors.root?.message}
      onSubmit={onSubmit}
      onOpenChange={onOpenChange}
    >
      <FormTextField
        control={form.control}
        name="name"
        label="Nome"
        id="role-name"
        autoFocus
      />
    </FormDialog>
  )
}
