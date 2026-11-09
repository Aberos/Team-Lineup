import { cn } from "@/lib/utils"

import { initialsOf } from "./card-display"

type PlayerPortraitProps = {
  name: string
  photoUrl: string | null
  className?: string
}

export function PlayerPortrait({ name, photoUrl, className }: PlayerPortraitProps) {
  if (photoUrl !== null) {
    return (
      <img
        src={photoUrl}
        alt=""
        className={cn("shrink-0 rounded-full object-cover", className)}
      />
    )
  }
  return (
    <span
      aria-hidden="true"
      className={cn(
        "flex shrink-0 items-center justify-center rounded-full font-extrabold",
        className,
      )}
    >
      {initialsOf(name)}
    </span>
  )
}
