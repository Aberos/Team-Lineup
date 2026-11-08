import { z } from "zod"

import { todayIso } from "@/lib/format"

const NAME_MAX_LENGTH = 100
const PHONE_MAX_LENGTH = 20
const EMAIL_MAX_LENGTH = 100
const NON_NEGATIVE_INTEGER = /^\d+$/

export const roleSchema = z.object({
  name: z
    .string()
    .trim()
    .min(1, "Informe o nome da função")
    .max(NAME_MAX_LENGTH, "Use no máximo 100 caracteres"),
})

export type RoleValues = z.infer<typeof roleSchema>

export const playerSchema = z.object({
  name: z
    .string()
    .trim()
    .min(1, "Informe o nome")
    .max(NAME_MAX_LENGTH, "Use no máximo 100 caracteres"),
  birthday: z
    .string()
    .min(1, "Informe a data de nascimento")
    .refine((value) => value <= todayIso(), "A data não pode estar no futuro"),
  phone: z
    .string()
    .trim()
    .min(1, "Informe o telefone")
    .max(PHONE_MAX_LENGTH, "Use no máximo 20 caracteres"),
  email: z
    .string()
    .trim()
    .max(EMAIL_MAX_LENGTH, "Use no máximo 100 caracteres")
    .pipe(z.email("Informe um e-mail válido")),
  number: z
    .string()
    .trim()
    .regex(NON_NEGATIVE_INTEGER, "Informe um número inteiro positivo")
    .transform(Number),
})

export type PlayerFormInput = z.input<typeof playerSchema>
export type PlayerFormOutput = z.output<typeof playerSchema>

export const playerRoleSchema = z.object({
  role_id: z.string().min(1, "Selecione uma função").transform(Number),
})

export type PlayerRoleFormInput = z.input<typeof playerRoleSchema>
export type PlayerRoleFormOutput = z.output<typeof playerRoleSchema>
