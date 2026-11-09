import { ImagePlus, Trash2 } from "lucide-react"
import { useRef, type ChangeEvent } from "react"
import { toast } from "sonner"

import { Button } from "@/components/ui/button"
import { apiErrorMessage } from "@/lib/form-errors"

import { useRemovePhoto, useUploadPhoto } from "./hooks"
import { PlayerPortrait } from "./PlayerPortrait"
import type { Player } from "./types"

const PHOTO_MAX_BYTES = 2 * 1024 * 1024
const PHOTO_TYPES = ["image/jpeg", "image/png", "image/webp"]

type PlayerPhotoFieldProps = {
  player: Player
}

export function PlayerPhotoField({ player }: PlayerPhotoFieldProps) {
  const inputRef = useRef<HTMLInputElement>(null)
  const uploadPhoto = useUploadPhoto(player.id)
  const removePhoto = useRemovePhoto(player.id)
  const isBusy = uploadPhoto.isPending || removePhoto.isPending
  const inputId = `player-${player.id}-photo`

  const handleFile = (event: ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    event.target.value = ""
    if (file === undefined) {
      return
    }
    if (!PHOTO_TYPES.includes(file.type)) {
      toast.error("Use uma imagem JPG, PNG ou WEBP.")
      return
    }
    if (file.size > PHOTO_MAX_BYTES) {
      toast.error("A foto deve ter no máximo 2 MB.")
      return
    }
    uploadPhoto.mutate(file, {
      onSuccess: () => toast.success("Foto atualizada"),
      onError: (error) =>
        toast.error(apiErrorMessage(error, "Não foi possível enviar a foto.")),
    })
  }

  const handleRemove = () => {
    removePhoto.mutate(undefined, {
      onSuccess: () => toast.success("Foto removida"),
      onError: () => toast.error("Não foi possível remover a foto."),
    })
  }

  return (
    <div className="flex flex-wrap items-center gap-4">
      <PlayerPortrait
        name={player.name}
        photoUrl={player.photo_url}
        className="size-20 border bg-muted text-2xl text-muted-foreground"
      />
      <div className="flex flex-col gap-2">
        <input
          ref={inputRef}
          id={inputId}
          type="file"
          accept={PHOTO_TYPES.join(",")}
          aria-label="Arquivo da foto do jogador"
          className="sr-only"
          onChange={handleFile}
        />
        <div className="flex flex-wrap gap-2">
          <Button
            type="button"
            variant="outline"
            size="sm"
            disabled={isBusy}
            onClick={() => inputRef.current?.click()}
          >
            <ImagePlus />
            {player.photo_url === null ? "Enviar foto" : "Trocar foto"}
          </Button>
          {player.photo_url !== null && (
            <Button
              type="button"
              variant="ghost"
              size="sm"
              disabled={isBusy}
              onClick={handleRemove}
            >
              <Trash2 />
              Remover foto
            </Button>
          )}
        </div>
        <p className="text-xs text-muted-foreground">
          JPG, PNG ou WEBP, até 2 MB.
        </p>
      </div>
    </div>
  )
}
