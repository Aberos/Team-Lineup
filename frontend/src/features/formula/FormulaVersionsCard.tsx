import { CircleAlert, FileCode, Play, Trash2 } from "lucide-react"
import { useState } from "react"
import { toast } from "sonner"

import { ConfirmDialog } from "@/components/common/ConfirmDialog"
import { EmptyState } from "@/components/common/EmptyState"
import { ErrorAlert } from "@/components/common/ErrorAlert"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { Skeleton } from "@/components/ui/skeleton"
import { ApiError } from "@/lib/api-client"
import { apiErrorMessage } from "@/lib/form-errors"
import { formatDateTime } from "@/lib/format"
import { useConfirmState } from "@/lib/use-confirm-state"

import { useActivateFormula, useDeleteFormula, useFormulas } from "./hooks"
import type {
  FormulaActivationErrorBody,
  FormulaFailure,
  OverallFormula,
} from "./types"

function isActivationError(body: unknown): body is FormulaActivationErrorBody {
  return (
    typeof body === "object" &&
    body !== null &&
    "failures" in body &&
    Array.isArray(body.failures)
  )
}

type FormulaVersionsCardProps = {
  onOpen: (formula: OverallFormula) => void
}

export function FormulaVersionsCard({ onOpen }: FormulaVersionsCardProps) {
  const formulas = useFormulas()
  const activate = useActivateFormula()
  const deleteFormula = useDeleteFormula()
  const confirmDelete = useConfirmState<OverallFormula>()
  const [failures, setFailures] = useState<{
    formulaId: number
    items: FormulaFailure[]
  } | null>(null)

  const handleActivate = (formula: OverallFormula) => {
    setFailures(null)
    activate.mutate(formula.id, {
      onSuccess: () =>
        toast.success(
          `Fórmula #${formula.id} ativada. As notas foram recalculadas.`,
        ),
      onError: (error) => {
        if (error instanceof ApiError && isActivationError(error.body)) {
          setFailures({ formulaId: formula.id, items: error.body.failures })
          return
        }
        toast.error(apiErrorMessage(error, "Não foi possível ativar a fórmula."))
      },
    })
  }

  const handleDelete = () => {
    const formula = confirmDelete.target
    if (formula === null) {
      return
    }
    deleteFormula.mutate(formula.id, {
      onSuccess: () => toast.success(`Versão #${formula.id} excluída`),
      onError: (error) =>
        toast.error(apiErrorMessage(error, "Não foi possível excluir a versão.")),
      onSettled: confirmDelete.close,
    })
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Versões</CardTitle>
        <CardDescription>
          Ativar roda a fórmula em todos os jogadores; se falhar em algum,
          nada muda.
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        {failures !== null && (
          <Alert variant="destructive">
            <CircleAlert />
            <AlertTitle>
              A fórmula #{failures.formulaId} falhou para alguns jogadores
            </AlertTitle>
            <AlertDescription>
              <ul className="list-disc pl-4">
                {failures.items.map((failure) => (
                  <li key={failure.player_id}>
                    {failure.player_name}: {failure.error}
                  </li>
                ))}
              </ul>
            </AlertDescription>
          </Alert>
        )}

        {formulas.isPending && <Skeleton className="h-24 w-full" />}
        {formulas.isError && (
          <ErrorAlert message="Não foi possível carregar as versões." />
        )}
        {formulas.isSuccess && formulas.data.length === 0 && (
          <EmptyState message="Nenhuma versão salva. A média simples está em uso." />
        )}
        {formulas.isSuccess && formulas.data.length > 0 && (
          <ul className="divide-y rounded-md border">
            {formulas.data.map((formula) => (
              <li
                key={formula.id}
                className="flex flex-wrap items-center justify-between gap-2 px-3 py-2"
              >
                <div className="min-w-0 space-y-0.5">
                  <p className="flex items-center gap-2 text-sm font-medium">
                    #{formula.id} {formula.description || "Sem descrição"}
                    {formula.is_active && <Badge>Em uso</Badge>}
                  </p>
                  <p className="text-xs text-muted-foreground">
                    {formula.created_by ?? "usuário removido"} ·{" "}
                    {formatDateTime(formula.created_at)}
                  </p>
                </div>
                <div className="flex gap-1">
                  <Button
                    variant="ghost"
                    size="icon"
                    aria-label={`Abrir versão ${formula.id} no editor`}
                    onClick={() => onOpen(formula)}
                  >
                    <FileCode />
                  </Button>
                  {!formula.is_active && (
                    <>
                      <Button
                        variant="ghost"
                        size="icon"
                        aria-label={`Ativar versão ${formula.id}`}
                        disabled={activate.isPending}
                        onClick={() => handleActivate(formula)}
                      >
                        <Play />
                      </Button>
                      <Button
                        variant="ghost"
                        size="icon"
                        aria-label={`Excluir versão ${formula.id}`}
                        onClick={() => confirmDelete.ask(formula)}
                      >
                        <Trash2 />
                      </Button>
                    </>
                  )}
                </div>
              </li>
            ))}
          </ul>
        )}
      </CardContent>
      <ConfirmDialog
        open={confirmDelete.open}
        title="Excluir versão?"
        description={`A versão #${confirmDelete.target?.id ?? ""} será removida do histórico.`}
        pending={deleteFormula.isPending}
        onConfirm={handleDelete}
        onOpenChange={confirmDelete.onOpenChange}
      />
    </Card>
  )
}
