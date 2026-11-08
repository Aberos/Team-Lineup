export type Event = {
  id: number
  name: string
  date: string
  location: string
}

export type EventPayload = Omit<Event, "id">

export type EventPlayer = {
  id: number
  name: string
  number: number
}

export type Participant = {
  player: EventPlayer
  score: number
}

export type ParticipantCreatePayload = { player_id: number; score: number }

export type ParticipantUpdatePayload = { score: number }

export type Team = { id: number; team_name: string }

export type TeamPayload = { team_name: string }

export type TeamMember = { player: EventPlayer }

export type TeamMemberPayload = { player_id: number }

export const MATCH_STATUS = {
  SCHEDULED: 0,
  ONGOING: 1,
  COMPLETED: 2,
} as const

export type MatchStatus = (typeof MATCH_STATUS)[keyof typeof MATCH_STATUS]

export const MATCH_STATUS_LABELS: Record<MatchStatus, string> = {
  [MATCH_STATUS.SCHEDULED]: "Agendada",
  [MATCH_STATUS.ONGOING]: "Em andamento",
  [MATCH_STATUS.COMPLETED]: "Encerrada",
}

export type Match = {
  id: number
  team_home: Team
  team_away: Team
  score_team_home: number
  score_team_away: number
  status: MatchStatus
}

export type MatchPayload = {
  team_home_id: number
  team_away_id: number
  score_team_home: number
  score_team_away: number
  status: MatchStatus
}
