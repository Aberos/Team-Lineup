import { zodResolver } from "@hookform/resolvers/zod"
import { useForm } from "react-hook-form"
import { useNavigate } from "react-router"

import { FormTextField } from "@/components/common/FormTextField"
import { Button } from "@/components/ui/button"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { FieldError, FieldGroup } from "@/components/ui/field"
import { applyApiErrors } from "@/lib/form-errors"

import { useLogin } from "./hooks"
import { loginSchema, type LoginValues } from "./schemas"

const LOGIN_FIELDS = ["username", "password"] as const

export function LoginPage() {
  const navigate = useNavigate()
  const login = useLogin()
  const form = useForm<LoginValues>({
    resolver: zodResolver(loginSchema),
    defaultValues: { username: "", password: "" },
  })

  const onSubmit = form.handleSubmit(async (values) => {
    try {
      await login.mutateAsync(values)
      navigate("/", { replace: true })
    } catch (error) {
      applyApiErrors(error, LOGIN_FIELDS, form.setError)
    }
  })

  return (
    <main className="flex min-h-svh items-center justify-center bg-muted/40 p-4">
      <Card className="w-full max-w-sm">
        <CardHeader>
          <CardTitle>Entrar no TeamLineup</CardTitle>
          <CardDescription>Use seu usuário e senha.</CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={onSubmit} noValidate>
            <FieldGroup>
              <FormTextField
                control={form.control}
                name="username"
                label="Usuário"
                id="login-username"
                autoComplete="username"
              />
              <FormTextField
                control={form.control}
                name="password"
                label="Senha"
                id="login-password"
                type="password"
                autoComplete="current-password"
              />
              {form.formState.errors.root && (
                <FieldError>{form.formState.errors.root.message}</FieldError>
              )}
              <Button
                type="submit"
                className="w-full"
                disabled={login.isPending}
              >
                Entrar
              </Button>
            </FieldGroup>
          </form>
        </CardContent>
      </Card>
    </main>
  )
}
