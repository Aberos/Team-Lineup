import { Plus } from "lucide-react"
import { useEffect, useState } from "react"
import { useSearchParams } from "react-router"

import { EmptyState } from "@/components/common/EmptyState"
import { ErrorAlert } from "@/components/common/ErrorAlert"
import { PageHeader } from "@/components/common/PageHeader"
import { Button } from "@/components/ui/button"
import { Field, FieldLabel } from "@/components/ui/field"
import { Input } from "@/components/ui/input"
import {
  NativeSelect,
  NativeSelectOption,
} from "@/components/ui/native-select"
import { Skeleton } from "@/components/ui/skeleton"
import { useDebouncedValue } from "@/lib/use-debounced-value"

import { usePlayerPages, useRoles } from "./hooks"
import { PlayerCardView } from "./PlayerCardView"
import { PlayerFormDialog } from "./PlayerFormDialog"
import { PLAYER_ORDERINGS, type PlayerOrdering } from "./types"

const DEFAULT_ORDERING: PlayerOrdering = "name"
const SKELETON_CARDS = 8
const CARD_GRID = "grid grid-cols-2 gap-3 sm:gap-4 md:grid-cols-3 lg:grid-cols-4"

function isPlayerOrdering(value: string | null): value is PlayerOrdering {
  return value !== null && value in PLAYER_ORDERINGS
}

function roleFromParams(value: string | null): number | null {
  return value !== null && /^\d+$/.test(value) ? Number(value) : null
}

export function PlayersPage() {
  const [searchParams, setSearchParams] = useSearchParams()
  const [searchText, setSearchText] = useState(searchParams.get("q") ?? "")
  const search = useDebouncedValue(searchText.trim())
  const role = roleFromParams(searchParams.get("role"))
  const orderingParam = searchParams.get("ordering")
  const ordering = isPlayerOrdering(orderingParam)
    ? orderingParam
    : DEFAULT_ORDERING
  const roles = useRoles()
  const players = usePlayerPages({ search, role, ordering })
  const [dialogOpen, setDialogOpen] = useState(false)

  useEffect(() => {
    setSearchParams(
      (current) => {
        const next = new URLSearchParams(current)
        if (search) {
          next.set("q", search)
        } else {
          next.delete("q")
        }
        return next
      },
      { replace: true },
    )
  }, [search, setSearchParams])

  const updateParam = (name: string, value: string) => {
    setSearchParams(
      (current) => {
        const next = new URLSearchParams(current)
        if (value) {
          next.set(name, value)
        } else {
          next.delete(name)
        }
        return next
      },
      { replace: true },
    )
  }

  const loaded = players.data?.pages.flatMap((page) => page.results) ?? []
  const total = players.data?.pages[0]?.count ?? 0

  return (
    <section className="space-y-4">
      <PageHeader
        title="Jogadores"
        description={
          players.isSuccess ? `${total} jogador(es) encontrado(s)` : undefined
        }
        actions={
          <Button onClick={() => setDialogOpen(true)}>
            <Plus />
            Novo jogador
          </Button>
        }
      />

      <div className="grid gap-3 sm:grid-cols-[minmax(0,1fr)_12rem_12rem]">
        <Field>
          <FieldLabel htmlFor="players-search">Buscar</FieldLabel>
          <Input
            id="players-search"
            type="search"
            placeholder="Nome do jogador"
            value={searchText}
            onChange={(event) => setSearchText(event.target.value)}
          />
        </Field>
        <Field>
          <FieldLabel htmlFor="players-role">Função</FieldLabel>
          <NativeSelect
            id="players-role"
            className="w-full"
            value={role === null ? "" : String(role)}
            onChange={(event) => updateParam("role", event.target.value)}
          >
            <NativeSelectOption value="">Todas</NativeSelectOption>
            {(roles.data ?? []).map((item) => (
              <NativeSelectOption key={item.id} value={String(item.id)}>
                {item.name}
              </NativeSelectOption>
            ))}
          </NativeSelect>
        </Field>
        <Field>
          <FieldLabel htmlFor="players-ordering">Ordenar por</FieldLabel>
          <NativeSelect
            id="players-ordering"
            className="w-full"
            value={ordering}
            onChange={(event) =>
              updateParam(
                "ordering",
                event.target.value === DEFAULT_ORDERING
                  ? ""
                  : event.target.value,
              )
            }
          >
            {Object.entries(PLAYER_ORDERINGS).map(([value, label]) => (
              <NativeSelectOption key={value} value={value}>
                {label}
              </NativeSelectOption>
            ))}
          </NativeSelect>
        </Field>
      </div>

      {players.isPending && (
        <div className={CARD_GRID} aria-label="Carregando jogadores">
          {Array.from({ length: SKELETON_CARDS }, (_, index) => (
            <Skeleton key={index} className="aspect-[2/3] w-full rounded-2xl" />
          ))}
        </div>
      )}

      {players.isError && (
        <ErrorAlert message="Não foi possível carregar os jogadores." />
      )}

      {players.isSuccess && loaded.length === 0 && (
        <EmptyState
          message={
            search || role !== null
              ? "Nenhum jogador encontrado com esses filtros."
              : "Nenhum jogador cadastrado."
          }
        />
      )}

      {players.isSuccess && loaded.length > 0 && (
        <ul className={CARD_GRID}>
          {loaded.map((player) => (
            <li key={player.id}>
              <PlayerCardView player={player} />
            </li>
          ))}
        </ul>
      )}

      {players.hasNextPage && (
        <div className="flex flex-col items-center gap-2">
          <p className="text-sm text-muted-foreground">
            Mostrando {loaded.length} de {total}
          </p>
          <Button
            variant="outline"
            disabled={players.isFetchingNextPage}
            onClick={() => players.fetchNextPage()}
          >
            {players.isFetchingNextPage ? "Carregando..." : "Carregar mais"}
          </Button>
        </div>
      )}

      <PlayerFormDialog
        open={dialogOpen}
        player={null}
        onOpenChange={setDialogOpen}
      />
    </section>
  )
}
