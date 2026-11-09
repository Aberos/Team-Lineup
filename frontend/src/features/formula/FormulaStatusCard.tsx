import { RotateCcw } from "lucide-react"
import { useState } from "react"
import { toast } from "sonner"

import { ConfirmDialog } from "@/components/common/ConfirmDialog"
import { ErrorAlert } from "@/components/common/ErrorAlert"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import {
  Card,
  CardAction,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { Skeleton } from "@/components/ui/skeleton"
import { formatDateTime } from "@/lib/format"

import { useActiveFormula, useDeactivateFormula } from "./hooks"

export function FormulaStatusCard() {
  const active = useActiveFormula()
  const deactivate = useDeactivateFormula()
  const [confirmOpen, setConfirmOpen] = useState(false)
  const formula = active.data?.formula ?? null

  const handleDeactivate = () => {
    deactivate.mutate(undefined, {
      onSuccess: () => toast.success("Voltando a usar a média simples"),
      onError: () => toast.error("Não foi possível desativar a fórmula."),
      onSettled: () => setConfirmOpen(false),
    })
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Em uso agora</CardTitle>
        <CardDescription>
          A nota geral de todos os jogadores é calculada por este método.
        </CardDescription>
        {formula !== null && (
          <CardAction>
            <Button variant="outline" onClick={() => setConfirmOpen(true)}>
              <RotateCcw />
              Usar média simples
            </Button>
          </CardAction>
        )}
      </CardHeader>
      <CardContent>
        {active.isPending && <Skeleton className="h-10 w-full" />}
        {active.isError && (
          <ErrorAlert message="Não foi possível carregar a fórmula em uso." />
        )}
        {active.isSuccess && formula === null && (
          <p className="text-sm">
            <Badge variant="secondary" className="mr-2">
              Média simples
            </Badge>
            Média das notas dos atributos da carta que foram avaliados.
          </p>
        )}
        {formula !== null && (
          <p className="text-sm">
            <Badge className="mr-2">Fórmula #{formula.id}</Badge>
            {formula.description || "Sem descrição"}
            <span className="block text-muted-foreground">
              Criada por {formula.created_by ?? "usuário removido"} em{" "}
              {formatDateTime(formula.created_at)}
            </span>
          </p>
        )}
      </CardContent>
      <ConfirmDialog
        open={confirmOpen}
        title="Voltar para a média simples?"
        description="A nota geral de todos os jogadores será recalculada pela média dos atributos da carta."
        confirmLabel="Usar média simples"
        pending={deactivate.isPending}
        onConfirm={handleDeactivate}
        onOpenChange={setConfirmOpen}
      />
    </Card>
  )
}
