import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"

import { playersApi, rolesApi } from "./api"
import type { PlayerPayload, RolePayload } from "./types"

const ROLES_KEY = ["players", "roles"] as const
const PLAYERS_KEY = ["players", "list"] as const

const playerKey = (id: number) => ["players", "detail", id] as const
const playerRolesKey = (id: number) => ["players", "detail", id, "roles"] as const

export function useRoles() {
  return useQuery({ queryKey: ROLES_KEY, queryFn: rolesApi.list })
}

export function useCreateRole() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (payload: RolePayload) => rolesApi.create(payload),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ROLES_KEY }),
  })
}

export function useUpdateRole() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ id, payload }: { id: number; payload: RolePayload }) =>
      rolesApi.update(id, payload),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ROLES_KEY }),
  })
}

export function useDeleteRole() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (id: number) => rolesApi.remove(id),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["players"] }),
  })
}

export function usePlayers() {
  return useQuery({ queryKey: PLAYERS_KEY, queryFn: playersApi.list })
}

export function usePlayer(id: number) {
  return useQuery({ queryKey: playerKey(id), queryFn: () => playersApi.get(id) })
}

export function useCreatePlayer() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (payload: PlayerPayload) => playersApi.create(payload),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: PLAYERS_KEY }),
  })
}

export function useUpdatePlayer() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ id, payload }: { id: number; payload: PlayerPayload }) =>
      playersApi.update(id, payload),
    onSuccess: (player) => {
      queryClient.setQueryData(playerKey(player.id), player)
      return queryClient.invalidateQueries({ queryKey: PLAYERS_KEY })
    },
  })
}

export function useDeletePlayer() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (id: number) => playersApi.remove(id),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: PLAYERS_KEY }),
  })
}

export function usePlayerRoles(id: number) {
  return useQuery({
    queryKey: playerRolesKey(id),
    queryFn: () => playersApi.listRoles(id),
  })
}

export function useAssignRole(playerId: number) {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (roleId: number) =>
      playersApi.assignRole(playerId, { role_id: roleId }),
    onSuccess: () =>
      queryClient.invalidateQueries({ queryKey: playerRolesKey(playerId) }),
  })
}

export function useRemoveRole(playerId: number) {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (roleId: number) => playersApi.removeRole(playerId, roleId),
    onSuccess: () =>
      queryClient.invalidateQueries({ queryKey: playerRolesKey(playerId) }),
  })
}
