import { Link } from "react-router"

import { cn } from "@/lib/utils"

import { splitColumns, tierFor } from "./card-display"
import { PlayerPortrait } from "./PlayerPortrait"
import type { CardAttribute, PlayerCard } from "./types"

type StatProps = {
  attribute: CardAttribute
}

function Stat({ attribute }: StatProps) {
  return (
    <div className="flex flex-row-reverse items-baseline justify-end gap-1 @[15rem]:gap-2">
      <dt
        title={attribute.name}
        className="text-xs font-semibold tracking-wide @[15rem]:text-lg"
      >
        {attribute.abbreviation}
      </dt>
      <dd className="min-w-[1.4em] text-right text-base font-extrabold tabular-nums @[15rem]:text-2xl">
        {attribute.value ?? "–"}
      </dd>
    </div>
  )
}

type PlayerCardViewProps = {
  player: PlayerCard
}

export function PlayerCardView({ player }: PlayerCardViewProps) {
  const tier = tierFor(player.overall)
  const primary = player.roles.find((role) => role.is_primary)
  const extraRoles = player.roles.filter((role) => !role.is_primary)
  const [left, right] = splitColumns(player.card_attributes)
  const overallText = player.overall === null ? "–" : String(player.overall)
  const roleNames = player.roles.map((role) => role.name).join(", ")
  const label = [
    player.name,
    `geral ${player.overall ?? "sem avaliação"}`,
    roleNames && `funções ${roleNames}`,
  ]
    .filter(Boolean)
    .join(", ")

  return (
    <Link
      to={`/players/${player.id}`}
      aria-label={label}
      className="group @container block rounded-2xl outline-none focus-visible:ring-3 focus-visible:ring-ring/60"
    >
      <article
        className={cn(
          "relative flex aspect-[2/3] flex-col overflow-hidden rounded-2xl font-card shadow-md transition-transform group-hover:-translate-y-0.5 group-hover:shadow-lg",
          tier.surface,
        )}
      >
        <div
          aria-hidden="true"
          className={cn(
            "pointer-events-none absolute inset-1.5 rounded-xl border @[15rem]:inset-2.5 @[15rem]:rounded-2xl",
            tier.line,
          )}
        />
        <div
          aria-hidden="true"
          className="pointer-events-none absolute inset-0 bg-linear-115 from-transparent from-35% via-white/15 via-48% to-transparent to-62%"
        />

        <div className="relative flex items-start justify-between px-3 pt-3.5 @[15rem]:px-5 @[15rem]:pt-5">
          <div className="flex min-w-9 flex-col items-center @[15rem]:min-w-14">
            <span className="text-4xl leading-[0.9] font-extrabold @[15rem]:text-6xl">
              {overallText}
            </span>
            <span className="text-sm leading-none font-bold tracking-wider @[15rem]:text-xl">
              {primary?.name ?? "–"}
            </span>
            <span
              aria-hidden="true"
              className={cn("my-1 h-px w-5 @[15rem]:my-1.5 @[15rem]:w-8", tier.divider)}
            />
            <span className="text-xs font-semibold @[15rem]:text-lg">
              #{player.number}
            </span>
          </div>
          <PlayerPortrait
            name={player.name}
            photoUrl={player.photo_url}
            className={cn(
              "size-16 border-2 bg-white/10 text-2xl @[15rem]:size-32 @[15rem]:border-3 @[15rem]:text-5xl",
              tier.ring,
            )}
          />
        </div>

        <p
          className={cn(
            "relative mx-3 mt-2.5 truncate border-y py-1 text-center text-base font-bold tracking-wide uppercase @[15rem]:mx-5 @[15rem]:mt-3.5 @[15rem]:py-2 @[15rem]:text-2xl",
            tier.line,
          )}
        >
          {player.name}
        </p>

        {player.card_attributes.length > 0 && (
          <div className="relative mx-3 mt-2 grid grid-cols-2 @[15rem]:mx-6 @[15rem]:mt-3">
            <dl
              className={cn(
                "flex flex-col gap-0.5 border-r pr-2 @[15rem]:gap-1 @[15rem]:pr-4",
                tier.line,
              )}
            >
              {left.map((attribute) => (
                <Stat key={attribute.abbreviation} attribute={attribute} />
              ))}
            </dl>
            <dl className="flex flex-col gap-0.5 pl-2 @[15rem]:gap-1 @[15rem]:pl-4">
              {right.map((attribute) => (
                <Stat key={attribute.abbreviation} attribute={attribute} />
              ))}
            </dl>
          </div>
        )}

        <div className="relative mt-auto flex flex-wrap justify-center gap-1 px-2 pb-3 @[15rem]:gap-1.5 @[15rem]:pb-5">
          {extraRoles.map((role) => (
            <span
              key={role.id}
              className={cn(
                "rounded-full border px-2 text-xs font-bold tracking-wide @[15rem]:text-sm",
                tier.line,
              )}
            >
              {role.name}
            </span>
          ))}
          <span
            className={cn(
              "rounded-full border bg-white/15 px-2 text-xs font-bold tracking-wider uppercase @[15rem]:text-sm",
              tier.line,
            )}
          >
            {tier.label}
          </span>
        </div>
      </article>
    </Link>
  )
}
