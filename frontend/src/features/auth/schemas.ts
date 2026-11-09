import { z } from "zod"

export const loginSchema = z.object({
  username: z.string().trim().min(1, "Informe o usuário"),
  password: z.string().min(1, "Informe a senha"),
  keepSignedIn: z.boolean(),
  rememberUsername: z.boolean(),
})

export type LoginValues = z.infer<typeof loginSchema>
