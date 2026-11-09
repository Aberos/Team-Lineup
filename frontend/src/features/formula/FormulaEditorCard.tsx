import { zodResolver } from "@hookform/resolvers/zod"
import { FlaskConical, Save } from "lucide-react"
import { Controller, useForm } from "react-hook-form"
import { toast } from "sonner"

import { FormTextField } from "@/components/common/FormTextField"
import { Button } from "@/components/ui/button"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import {
  Field,
  FieldDescription,
  FieldError,
  FieldGroup,
  FieldLabel,
} from "@/components/ui/field"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import { applyApiErrors } from "@/lib/form-errors"

import { PREVIEW_LIMIT, useCreateFormula, usePreviewFormula } from "./hooks"
import { LuaEditor } from "./LuaEditor"
import { formulaSchema, type FormulaValues } from "./schemas"

const FORMULA_FIELDS = ["script", "description"] as const

type FormulaEditorCardProps = {
  initialValues: FormulaValues
}

export function FormulaEditorCard({ initialValues }: FormulaEditorCardProps) {
  const createFormula = useCreateFormula()
  const preview = usePreviewFormula()
  const form = useForm<FormulaValues>({
    resolver: zodResolver(formulaSchema),
    defaultValues: initialValues,
  })

  const handlePreview = form.handleSubmit(async ({ script }) => {
    try {
      await preview.mutateAsync(script)
    } catch (error) {
      applyApiErrors(error, FORMULA_FIELDS, form.setError)
    }
  })

  const handleSave = form.handleSubmit(async (values) => {
    try {
      const formula = await createFormula.mutateAsync(values)
      toast.success(`Versão #${formula.id} salva. Ative-a na lista de versões.`)
    } catch (error) {
      applyApiErrors(error, FORMULA_FIELDS, form.setError)
    }
  })

  return (
    <Card>
      <CardHeader>
        <CardTitle>Editor</CardTitle>
        <CardDescription>
          Teste o script com jogadores reais antes de salvar. Salvar cria uma
          nova versão, que só passa a valer depois de ativada.
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        <form onSubmit={handleSave} noValidate>
          <FieldGroup>
            <FormTextField
              control={form.control}
              name="description"
              label="Descrição da versão"
              id="formula-description"
            />
            <Controller
              name="script"
              control={form.control}
              render={({ field, fieldState }) => (
                <Field data-invalid={fieldState.invalid}>
                  <FieldLabel id="formula-script-label">Script Lua</FieldLabel>
                  <LuaEditor
                    id="formula-script"
                    labelId="formula-script-label"
                    descriptionId="formula-script-description"
                    value={field.value}
                    invalid={fieldState.invalid}
                    onChange={field.onChange}
                    onBlur={field.onBlur}
                  />
                  <FieldDescription id="formula-script-description">
                    Defina a função overall(notas, funcoes, principal). Tab
                    indenta; para sair do editor pelo teclado, pressione Esc e
                    depois Tab.
                  </FieldDescription>
                  {fieldState.invalid && (
                    <FieldError errors={[fieldState.error]} />
                  )}
                </Field>
              )}
            />
            {form.formState.errors.root && (
              <FieldError>{form.formState.errors.root.message}</FieldError>
            )}
            <div className="flex flex-wrap gap-2">
              <Button
                type="button"
                variant="outline"
                disabled={preview.isPending}
                onClick={handlePreview}
              >
                <FlaskConical />
                {preview.isPending ? "Testando..." : "Testar com jogadores"}
              </Button>
              <Button type="submit" disabled={createFormula.isPending}>
                <Save />
                Salvar versão
              </Button>
            </div>
          </FieldGroup>
        </form>

        {preview.isSuccess && (
          <div className="space-y-2">
            <h3 className="text-sm font-medium">
              Resultado com os primeiros {PREVIEW_LIMIT} jogadores
            </h3>
            {preview.data.length === 0 ? (
              <p className="text-sm text-muted-foreground">
                Nenhum jogador cadastrado para testar.
              </p>
            ) : (
              <div className="overflow-x-auto">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Jogador</TableHead>
                      <TableHead className="w-20 text-center">Atual</TableHead>
                      <TableHead className="w-20 text-center">Nova</TableHead>
                      <TableHead>Erro</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {preview.data.map((row) => (
                      <TableRow key={row.player_id}>
                        <TableCell>{row.player_name}</TableCell>
                        <TableCell className="text-center tabular-nums">
                          {row.current_overall ?? "–"}
                        </TableCell>
                        <TableCell className="text-center font-semibold tabular-nums">
                          {row.error === null ? (row.new_overall ?? "–") : "–"}
                        </TableCell>
                        <TableCell className="text-sm text-destructive">
                          {row.error}
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </div>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  )
}
