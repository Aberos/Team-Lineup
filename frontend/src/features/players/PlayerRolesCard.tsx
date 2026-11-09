import { zodResolver } from "@hookform/resolvers/zod"
import { Plus, Star, X } from "lucide-react"
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

import {
  useAssignRole,
  usePlayerRoles,
  useRemoveRole,
  useRoles,
  useSetPrimaryRole,
} from "./hooks"
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
  const setPrimaryRole = useSetPrimaryRole(playerId)
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

  const handleSetPrimary = (roleId: number, roleName: string) => {
    setPrimaryRole.mutate(roleId, {
      onSuccess: () => toast.success(`"${roleName}" agora é a função principal`),
      onError: () => toast.error("Não foi possível alterar a função principal."),
    })
  }

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
        <CardDescription>
          Posições em que o jogador atua. A principal aparece na carta.
        </CardDescription>
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
          <ul className="divide-y rounded-md border">
            {playerRoles.data.map((role) => (
              <li
                key={role.id}
                className="flex items-center justify-between gap-2 px-3 py-1.5"
              >
                <span className="flex items-center gap-2 text-sm font-medium">
                  {role.name}
                  {role.is_primary && <Badge>Principal</Badge>}
                </span>
                <span className="flex">
                  {!role.is_primary && (
                    <Button
                      variant="ghost"
                      size="icon"
                      aria-label={`Tornar ${role.name} a função principal`}
                      disabled={setPrimaryRole.isPending}
                      onClick={() => handleSetPrimary(role.id, role.name)}
                    >
                      <Star />
                    </Button>
                  )}
                  <Button
                    variant="ghost"
                    size="icon"
                    aria-label={`Remover ${role.name}`}
                    disabled={removeRole.isPending}
                    onClick={() => handleRemove(role.id, role.name)}
                  >
                    <X />
                  </Button>
                </span>
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
