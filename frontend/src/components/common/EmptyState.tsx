type EmptyStateProps = {
  message: string
}

export function EmptyState({ message }: EmptyStateProps) {
  return (
    <p className="rounded-md border border-dashed p-6 text-center text-sm text-muted-foreground">
      {message}
    </p>
  )
}
