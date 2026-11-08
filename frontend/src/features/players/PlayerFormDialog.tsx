import { zodResolver } from "@hookform/resolvers/zod"
import { useEffect } from "react"
import { useForm } from "react-hook-form"
import { toast } from "sonner"

import { FormDialog } from "@/components/common/FormDialog"
import { FormTextField } from "@/components/common/FormTextField"
import { applyApiErrors } from "@/lib/form-errors"

import { useCreatePlayer, useUpdatePlayer } from "./hooks"
import {
  playerSchema,
  type PlayerFormInput,
  type PlayerFormOutput,
} from "./schemas"
import type { Player } from "./types"

const PLAYER_FIELDS = ["name", "birthday", "phone", "email", "number"] as const

const EMPTY_VALUES: PlayerFormInput = {
  name: "",
  birthday: "",
  phone: "",
  email: "",
  number: "",
}

function toFormValues(player: Player | null): PlayerFormInput {
  if (player === null) {
    return EMPTY_VALUES
  }
  return {
    name: player.name,
    birthday: player.birthday,
    phone: player.phone,
    email: player.email,
    number: String(player.number),
  }
}

type PlayerFormDialogProps = {
  open: boolean
  player: Player | null
  onOpenChange: (open: boolean) => void
}

export function PlayerFormDialog({
  open,
  player,
  onOpenChange,
}: PlayerFormDialogProps) {
  const createPlayer = useCreatePlayer()
  const updatePlayer = useUpdatePlayer()
  const isPending = createPlayer.isPending || updatePlayer.isPending
  const form = useForm<PlayerFormInput, unknown, PlayerFormOutput>({
    resolver: zodResolver(playerSchema),
    defaultValues: EMPTY_VALUES,
  })

  useEffect(() => {
    if (open) {
      form.reset(toFormValues(player))
    }
  }, [open, player, form])

  const onSubmit = form.handleSubmit(async (values) => {
    try {
      if (player === null) {
        await createPlayer.mutateAsync(values)
        toast.success("Jogador cadastrado")
      } else {
        await updatePlayer.mutateAsync({ id: player.id, payload: values })
        toast.success("Jogador atualizado")
      }
      onOpenChange(false)
    } catch (error) {
      applyApiErrors(error, PLAYER_FIELDS, form.setError)
    }
  })

  return (
    <FormDialog
      open={open}
      title={player === null ? "Novo jogador" : "Editar jogador"}
      description="Dados de contato e camisa."
      pending={isPending}
      rootError={form.formState.errors.root?.message}
      onSubmit={onSubmit}
      onOpenChange={onOpenChange}
    >
      <FormTextField
        control={form.control}
        name="name"
        label="Nome"
        id="player-name"
        autoFocus
      />
      <div className="grid gap-4 sm:grid-cols-2">
        <FormTextField
          control={form.control}
          name="birthday"
          label="Nascimento"
          id="player-birthday"
          type="date"
        />
        <FormTextField
          control={form.control}
          name="number"
          label="Número"
          id="player-number"
          inputMode="numeric"
        />
      </div>
      <FormTextField
        control={form.control}
        name="phone"
        label="Telefone"
        id="player-phone"
        type="tel"
        inputMode="tel"
        autoComplete="tel"
      />
      <FormTextField
        control={form.control}
        name="email"
        label="E-mail"
        id="player-email"
        type="email"
        inputMode="email"
        autoComplete="email"
      />
    </FormDialog>
  )
}
