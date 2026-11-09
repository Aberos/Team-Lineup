import { useState } from "react"

import { PageHeader } from "@/components/common/PageHeader"
import { Skeleton } from "@/components/ui/skeleton"

import { FormulaEditorCard } from "./FormulaEditorCard"
import { FormulaHelpCard } from "./FormulaHelpCard"
import { FormulaStatusCard } from "./FormulaStatusCard"
import { FormulaVersionsCard } from "./FormulaVersionsCard"
import { useActiveFormula } from "./hooks"
import type { FormulaValues } from "./schemas"
import { FORMULA_TEMPLATE } from "./template"
import type { OverallFormula } from "./types"

type Draft = { key: string; values: FormulaValues }

export function FormulaPage() {
  const active = useActiveFormula()
  const [draft, setDraft] = useState<Draft | null>(null)

  const activeFormula = active.data?.formula ?? null
  const currentDraft: Draft = draft ?? {
    key: activeFormula === null ? "template" : `active-${activeFormula.id}`,
    values: {
      script: activeFormula?.script ?? FORMULA_TEMPLATE,
      description: "",
    },
  }

  const openInEditor = (formula: OverallFormula) => {
    setDraft({
      key: `version-${formula.id}-${Date.now()}`,
      values: {
        script: formula.script,
        description: formula.description,
      },
    })
  }

  return (
    <section className="space-y-4">
      <PageHeader
        title="Fórmula da nota geral"
        description="Defina em Lua como a nota geral dos jogadores é calculada."
      />
      <FormulaStatusCard />
      <div className="grid gap-4 lg:grid-cols-[minmax(0,1fr)_22rem]">
        <div className="min-w-0 space-y-4">
          {active.isPending ? (
            <Skeleton className="h-96 w-full" />
          ) : (
            <FormulaEditorCard
              key={currentDraft.key}
              initialValues={currentDraft.values}
            />
          )}
          <FormulaVersionsCard onOpen={openInEditor} />
        </div>
        <FormulaHelpCard />
      </div>
    </section>
  )
}
