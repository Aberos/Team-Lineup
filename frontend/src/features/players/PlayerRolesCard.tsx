import { zodResolver } from "@hookform/resolvers/zod"
import { Plus, X } from "lucide-react"
import { useForm } from "react-hook-form"
import { toast } from "sonner"

import { EmptyState } from "@/components/common/EmptyState"
import { FormSelectField } from "@/components/common/FormSelectField"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { FieldError } from "@/components/ui/field"
import { Skeleton } from "@/components/ui/skeleton"
import { applyApiErrors } from "@/lib/form-errors"

import { useAssignRole, usePlayerRoles, useRemoveRole, useRoles } from "./hooks"
import {
  playerRoleSchema,
  type PlayerRoleFormInput,
  type PlayerRoleFormOutput,
} from "./schemas"

const ROLE_FIELDS = ["role_id"] as const

type PlayerRolesCardProps = {
  playerId: number
}

export function PlayerRolesCard({ playerId }: PlayerRolesCardProps) {
  const playerRoles = usePlayerRoles(playerId)
  const roles = useRoles()
  const assignRole = useAssignRole(playerId)
  const removeRole = useRemoveRole(playerId)
  const form = useForm<PlayerRoleFormInput, unknown, PlayerRoleFormOutput>({
    resolver: zodResolver(playerRoleSchema),
    defaultValues: { role_id: "" },
  })

  const assignedIds = new Set(playerRoles.data?.map((role) => role.id))
  const availableOptions = (roles.data ?? [])
    .filter((role) => !assignedIds.has(role.id))
    .map((role) => ({ value: String(role.id), label: role.name }))

  const onSubmit = form.handleSubmit(async ({ role_id: roleId }) => {
    try {
      await assignRole.mutateAsync(roleId)
      form.reset({ role_id: "" })
      toast.success("Função atribuída")
    } catch (error) {
      applyApiErrors(error, ROLE_FIELDS, form.setError)
    }
  })

  const handleRemove = (roleId: number, roleName: string) => {
    removeRole.mutate(roleId, {
      onSuccess: () => toast.success(`Função "${roleName}" removida`),
      onError: () => toast.error("Não foi possível remover a função."),
    })
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Funções</CardTitle>
        <CardDescription>Posições em que o jogador atua.</CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        {playerRoles.isPending && <Skeleton className="h-8 w-full" />}
        {playerRoles.isError && (
          <p className="text-sm text-destructive">
            Não foi possível carregar as funções do jogador.
          </p>
        )}
        {playerRoles.isSuccess && playerRoles.data.length === 0 && (
          <EmptyState message="Nenhuma função atribuída." />
        )}
        {playerRoles.isSuccess && playerRoles.data.length > 0 && (
          <ul className="flex flex-wrap gap-2">
            {playerRoles.data.map((role) => (
              <li key={role.id}>
                <Badge variant="secondary" className="gap-1 pr-1">
                  {role.name}
                  <button
                    type="button"
                    className="rounded-sm p-0.5 hover:bg-muted-foreground/20"
                    aria-label={`Remover ${role.name}`}
                    disabled={removeRole.isPending}
                    onClick={() => handleRemove(role.id, role.name)}
                  >
                    <X className="size-3" />
                  </button>
                </Badge>
              </li>
            ))}
          </ul>
        )}
        <form
          onSubmit={onSubmit}
          noValidate
          className="flex flex-col gap-2 sm:flex-row sm:items-end"
        >
          <div className="flex-1">
            <FormSelectField
              control={form.control}
              name="role_id"
              label="Atribuir função"
              id="player-role"
              options={availableOptions}
              placeholder="Selecione"
            />
          </div>
          <Button
            type="submit"
            disabled={assignRole.isPending || availableOptions.length === 0}
          >
            <Plus />
            Atribuir
          </Button>
        </form>
        {form.formState.errors.root && (
          <FieldError>{form.formState.errors.root.message}</FieldError>
        )}
      </CardContent>
    </Card>
  )
}
