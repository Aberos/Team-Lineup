import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"

import { FORMULA_TEMPLATE } from "./template"

const PARAMETERS = [
  {
    name: "notas",
    text: "tabela com as notas do jogador nos atributos da carta, pela sigla (ex.: notas.VEL, notas[\"FÍS\"]). Atributos sem nota não aparecem.",
  },
  {
    name: "funcoes",
    text: "lista com os nomes das funções do jogador, a principal primeiro.",
  },
  {
    name: "principal",
    text: "nome da função principal, ou nil quando o jogador não tem função.",
  },
] as const

export function FormulaHelpCard() {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Como escrever a fórmula</CardTitle>
        <CardDescription>
          O script roda em um ambiente isolado, com limite de tempo e memória.
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4 text-sm">
        <ul className="space-y-2">
          {PARAMETERS.map((parameter) => (
            <li key={parameter.name}>
              <code className="rounded bg-muted px-1 py-0.5 font-mono">
                {parameter.name}
              </code>{" "}
              {parameter.text}
            </li>
          ))}
        </ul>
        <p>
          Retorne um número de 0 a 100 (é arredondado) ou nil para "sem
          avaliação". Disponível: math, string, table, pairs, ipairs, tonumber,
          tostring, type, error e assert. Sem acesso a arquivos, rede, sistema
          ou números aleatórios.
        </p>
        <div className="space-y-1">
          <p className="font-medium">Exemplo: pesos por função principal</p>
          <pre className="overflow-x-auto rounded-md bg-muted p-3 font-mono text-xs leading-relaxed">
            {FORMULA_TEMPLATE}
          </pre>
        </div>
      </CardContent>
    </Card>
  )
}
