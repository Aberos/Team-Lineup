import { z } from "zod"

import { MATCH_STATUS, type MatchStatus } from "./types"

const TEXT_MAX_LENGTH = 100
const INTEGER = /^-?\d+$/
const NON_NEGATIVE_INTEGER = /^\d+$/
const MATCH_STATUS_VALUES: ReadonlyArray<string> = Object.values(
  MATCH_STATUS,
).map(String)

const requiredId = (message: string) =>
  z.string().min(1, message).transform(Number)

const integerText = z
  .string()
  .trim()
  .regex(INTEGER, "Informe um número inteiro")
  .transform(Number)

const scoreText = z
  .string()
  .trim()
  .regex(NON_NEGATIVE_INTEGER, "Informe um placar válido")
  .transform(Number)

export const eventSchema = z.object({
  name: z
    .string()
    .trim()
    .min(1, "Informe o nome do evento")
    .max(TEXT_MAX_LENGTH, "Use no máximo 100 caracteres"),
  date: z.string().min(1, "Informe a data"),
  location: z
    .string()
    .trim()
    .min(1, "Informe o local")
    .max(TEXT_MAX_LENGTH, "Use no máximo 100 caracteres"),
})

export type EventFormValues = z.infer<typeof eventSchema>

export const participantSchema = z.object({
  player_id: requiredId("Selecione um jogador"),
  score: integerText,
})

export type ParticipantFormInput = z.input<typeof participantSchema>
export type ParticipantFormOutput = z.output<typeof participantSchema>

export const scoreSchema = z.object({ score: integerText })

export type ScoreFormInput = z.input<typeof scoreSchema>
export type ScoreFormOutput = z.output<typeof scoreSchema>

export const teamSchema = z.object({
  team_name: z
    .string()
    .trim()
    .min(1, "Informe o nome do time")
    .max(TEXT_MAX_LENGTH, "Use no máximo 100 caracteres"),
})

export type TeamFormValues = z.infer<typeof teamSchema>

export const memberSchema = z.object({
  player_id: requiredId("Selecione um participante"),
})

export type MemberFormInput = z.input<typeof memberSchema>
export type MemberFormOutput = z.output<typeof memberSchema>

export const matchSchema = z
  .object({
    team_home_id: requiredId("Selecione o mandante"),
    team_away_id: requiredId("Selecione o visitante"),
    score_team_home: scoreText,
    score_team_away: scoreText,
    status: z
      .string()
      .refine((value) => MATCH_STATUS_VALUES.includes(value), "Status inválido")
      .transform((value) => Number(value) as MatchStatus),
  })
  .refine((values) => values.team_home_id !== values.team_away_id, {
    message: "Os times precisam ser diferentes",
    path: ["team_away_id"],
  })

export type MatchFormInput = z.input<typeof matchSchema>
export type MatchFormOutput = z.output<typeof matchSchema>
