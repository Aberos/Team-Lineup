import { useState } from "react"

export function useConfirmState<T>() {
  const [target, setTarget] = useState<T | null>(null)
  return {
    target,
    open: target !== null,
    ask: (item: T) => setTarget(item),
    onOpenChange: (open: boolean) => {
      if (!open) {
        setTarget(null)
      }
    },
    close: () => setTarget(null),
  }
}
