import { zodResolver } from "@hookform/resolvers/zod"
import { useForm } from "react-hook-form"
import { useNavigate } from "react-router"

import { FormCheckboxField } from "@/components/common/FormCheckboxField"
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
import { authStorage } from "@/lib/auth-storage"
import { applyApiErrors } from "@/lib/form-errors"

import { useLogin } from "./hooks"
import { loginSchema, type LoginValues } from "./schemas"

const LOGIN_FIELDS = ["username", "password"] as const

function initialValues(): LoginValues {
  const rememberedUsername = authStorage.getRememberedUsername()
  return {
    username: rememberedUsername ?? "",
    password: "",
    keepSignedIn: false,
    rememberUsername: rememberedUsername !== null,
  }
}

export function LoginPage() {
  const navigate = useNavigate()
  const login = useLogin()
  const form = useForm<LoginValues>({
    resolver: zodResolver(loginSchema),
    defaultValues: initialValues(),
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
                autoFocus={authStorage.getRememberedUsername() !== null}
              />
              <div className="flex flex-col gap-3">
                <FormCheckboxField
                  control={form.control}
                  name="keepSignedIn"
                  label="Manter conectado"
                  id="login-keep-signed-in"
                />
                <FormCheckboxField
                  control={form.control}
                  name="rememberUsername"
                  label="Lembrar meu usuário"
                  id="login-remember-username"
                />
              </div>
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
