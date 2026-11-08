import {
  useMutation,
  useQueries,
  useQuery,
  useQueryClient,
} from "@tanstack/react-query"

import { eventsApi, matchesApi, participantsApi, teamsApi } from "./api"
import type {
  EventPayload,
  MatchPayload,
  ParticipantCreatePayload,
  TeamMember,
} from "./types"

const EVENTS_LIST_KEY = ["events", "list"] as const

const eventKey = (eventId: number) => ["events", "detail", eventId] as const
const eventInfoKey = (eventId: number) =>
  [...eventKey(eventId), "info"] as const
const participantsKey = (eventId: number) =>
  [...eventKey(eventId), "participants"] as const
const teamsKey = (eventId: number) => [...eventKey(eventId), "teams"] as const
const membersKey = (eventId: number, teamId: number) =>
  [...eventKey(eventId), "members", teamId] as const
const matchesKey = (eventId: number) =>
  [...eventKey(eventId), "matches"] as const

function useInvalidateEvent(eventId: number) {
  const queryClient = useQueryClient()
  return () => queryClient.invalidateQueries({ queryKey: eventKey(eventId) })
}

export function useEvents() {
  return useQuery({ queryKey: EVENTS_LIST_KEY, queryFn: eventsApi.list })
}

export function useEvent(eventId: number) {
  return useQuery({
    queryKey: eventInfoKey(eventId),
    queryFn: () => eventsApi.get(eventId),
  })
}

export function useCreateEvent() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (payload: EventPayload) => eventsApi.create(payload),
    onSuccess: () =>
      queryClient.invalidateQueries({ queryKey: EVENTS_LIST_KEY }),
  })
}

export function useUpdateEvent() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ id, payload }: { id: number; payload: EventPayload }) =>
      eventsApi.update(id, payload),
    onSuccess: (event) => {
      queryClient.setQueryData(eventInfoKey(event.id), event)
      return queryClient.invalidateQueries({ queryKey: EVENTS_LIST_KEY })
    },
  })
}

export function useDeleteEvent() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (eventId: number) => eventsApi.remove(eventId),
    onSuccess: () =>
      queryClient.invalidateQueries({ queryKey: EVENTS_LIST_KEY }),
  })
}

export function useParticipants(eventId: number) {
  return useQuery({
    queryKey: participantsKey(eventId),
    queryFn: () => participantsApi.list(eventId),
  })
}

export function useAddParticipant(eventId: number) {
  const invalidate = useInvalidateEvent(eventId)
  return useMutation({
    mutationFn: (payload: ParticipantCreatePayload) =>
      participantsApi.add(eventId, payload),
    onSuccess: invalidate,
  })
}

export function useUpdateScore(eventId: number) {
  const invalidate = useInvalidateEvent(eventId)
  return useMutation({
    mutationFn: ({ playerId, score }: { playerId: number; score: number }) =>
      participantsApi.updateScore(eventId, playerId, { score }),
    onSuccess: invalidate,
  })
}

export function useRemoveParticipant(eventId: number) {
  const invalidate = useInvalidateEvent(eventId)
  return useMutation({
    mutationFn: (playerId: number) => participantsApi.remove(eventId, playerId),
    onSuccess: invalidate,
  })
}

export function useTeams(eventId: number) {
  return useQuery({
    queryKey: teamsKey(eventId),
    queryFn: () => teamsApi.list(eventId),
  })
}

export function useTeamMembers(
  eventId: number,
  teamIds: ReadonlyArray<number>,
) {
  return useQueries({
    queries: teamIds.map((teamId) => ({
      queryKey: membersKey(eventId, teamId),
      queryFn: () => teamsApi.listMembers(eventId, teamId),
    })),
    combine: (results) => {
      const membersByTeam = new Map<number, TeamMember[]>()
      teamIds.forEach((teamId, index) => {
        membersByTeam.set(teamId, results[index]?.data ?? [])
      })
      return {
        membersByTeam,
        isPending: results.some((result) => result.isPending),
        isError: results.some((result) => result.isError),
      }
    },
  })
}

export function useSaveTeam(eventId: number) {
  const invalidate = useInvalidateEvent(eventId)
  return useMutation({
    mutationFn: ({
      teamId,
      teamName,
    }: {
      teamId: number | null
      teamName: string
    }) =>
      teamId === null
        ? teamsApi.create(eventId, { team_name: teamName })
        : teamsApi.rename(eventId, teamId, { team_name: teamName }),
    onSuccess: invalidate,
  })
}

export function useDeleteTeam(eventId: number) {
  const invalidate = useInvalidateEvent(eventId)
  return useMutation({
    mutationFn: (teamId: number) => teamsApi.remove(eventId, teamId),
    onSuccess: invalidate,
  })
}

export function useAddMember(eventId: number) {
  const invalidate = useInvalidateEvent(eventId)
  return useMutation({
    mutationFn: ({ teamId, playerId }: { teamId: number; playerId: number }) =>
      teamsApi.addMember(eventId, teamId, { player_id: playerId }),
    onSuccess: invalidate,
  })
}

export function useRemoveMember(eventId: number) {
  const invalidate = useInvalidateEvent(eventId)
  return useMutation({
    mutationFn: ({ teamId, playerId }: { teamId: number; playerId: number }) =>
      teamsApi.removeMember(eventId, teamId, playerId),
    onSuccess: invalidate,
  })
}

export function useMatches(eventId: number) {
  return useQuery({
    queryKey: matchesKey(eventId),
    queryFn: () => matchesApi.list(eventId),
  })
}

export function useSaveMatch(eventId: number) {
  const invalidate = useInvalidateEvent(eventId)
  return useMutation({
    mutationFn: ({
      matchId,
      payload,
    }: {
      matchId: number | null
      payload: MatchPayload
    }) =>
      matchId === null
        ? matchesApi.create(eventId, payload)
        : matchesApi.update(eventId, matchId, payload),
    onSuccess: invalidate,
  })
}

export function useDeleteMatch(eventId: number) {
  const invalidate = useInvalidateEvent(eventId)
  return useMutation({
    mutationFn: (matchId: number) => matchesApi.remove(eventId, matchId),
    onSuccess: invalidate,
  })
}
