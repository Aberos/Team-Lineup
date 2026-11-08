import { apiRequest } from "@/lib/api-client"

import type {
  Event,
  EventPayload,
  Match,
  MatchPayload,
  Participant,
  ParticipantCreatePayload,
  ParticipantUpdatePayload,
  Team,
  TeamMember,
  TeamMemberPayload,
  TeamPayload,
} from "./types"

const EVENT_PATH = "/event/"

const eventUrl = (eventId: number) => `${EVENT_PATH}${eventId}/`
const participantsUrl = (eventId: number) =>
  `${eventUrl(eventId)}participant/`
const teamsUrl = (eventId: number) => `${eventUrl(eventId)}team/`
const teamUrl = (eventId: number, teamId: number) =>
  `${teamsUrl(eventId)}${teamId}/`
const membersUrl = (eventId: number, teamId: number) =>
  `${teamUrl(eventId, teamId)}member/`
const matchesUrl = (eventId: number) => `${eventUrl(eventId)}match/`

export const eventsApi = {
  list: () => apiRequest<Event[]>(EVENT_PATH),
  get: (eventId: number) => apiRequest<Event>(eventUrl(eventId)),
  create: (payload: EventPayload) =>
    apiRequest<Event>(EVENT_PATH, { method: "POST", body: payload }),
  update: (eventId: number, payload: EventPayload) =>
    apiRequest<Event>(eventUrl(eventId), { method: "PUT", body: payload }),
  remove: (eventId: number) =>
    apiRequest<null>(eventUrl(eventId), { method: "DELETE" }),
}

export const participantsApi = {
  list: (eventId: number) =>
    apiRequest<Participant[]>(participantsUrl(eventId)),
  add: (eventId: number, payload: ParticipantCreatePayload) =>
    apiRequest<Participant>(participantsUrl(eventId), {
      method: "POST",
      body: payload,
    }),
  updateScore: (
    eventId: number,
    playerId: number,
    payload: ParticipantUpdatePayload,
  ) =>
    apiRequest<Participant>(`${participantsUrl(eventId)}${playerId}/`, {
      method: "PUT",
      body: payload,
    }),
  remove: (eventId: number, playerId: number) =>
    apiRequest<null>(`${participantsUrl(eventId)}${playerId}/`, {
      method: "DELETE",
    }),
}

export const teamsApi = {
  list: (eventId: number) => apiRequest<Team[]>(teamsUrl(eventId)),
  create: (eventId: number, payload: TeamPayload) =>
    apiRequest<Team>(teamsUrl(eventId), { method: "POST", body: payload }),
  rename: (eventId: number, teamId: number, payload: TeamPayload) =>
    apiRequest<Team>(teamUrl(eventId, teamId), {
      method: "PUT",
      body: payload,
    }),
  remove: (eventId: number, teamId: number) =>
    apiRequest<null>(teamUrl(eventId, teamId), { method: "DELETE" }),
  listMembers: (eventId: number, teamId: number) =>
    apiRequest<TeamMember[]>(membersUrl(eventId, teamId)),
  addMember: (eventId: number, teamId: number, payload: TeamMemberPayload) =>
    apiRequest<TeamMember>(membersUrl(eventId, teamId), {
      method: "POST",
      body: payload,
    }),
  removeMember: (eventId: number, teamId: number, playerId: number) =>
    apiRequest<null>(`${membersUrl(eventId, teamId)}${playerId}/`, {
      method: "DELETE",
    }),
}

export const matchesApi = {
  list: (eventId: number) => apiRequest<Match[]>(matchesUrl(eventId)),
  create: (eventId: number, payload: MatchPayload) =>
    apiRequest<Match>(matchesUrl(eventId), { method: "POST", body: payload }),
  update: (eventId: number, matchId: number, payload: MatchPayload) =>
    apiRequest<Match>(`${matchesUrl(eventId)}${matchId}/`, {
      method: "PUT",
      body: payload,
    }),
  remove: (eventId: number, matchId: number) =>
    apiRequest<null>(`${matchesUrl(eventId)}${matchId}/`, {
      method: "DELETE",
    }),
}
