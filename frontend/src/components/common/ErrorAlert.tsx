import { CircleAlert } from "lucide-react"

import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"

type ErrorAlertProps = {
  message: string
}

export function ErrorAlert({ message }: ErrorAlertProps) {
  return (
    <Alert variant="destructive">
      <CircleAlert />
      <AlertTitle>Erro ao carregar</AlertTitle>
      <AlertDescription>{message}</AlertDescription>
    </Alert>
  )
}
