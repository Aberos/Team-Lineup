import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"

import { attributesApi, playersApi, rolesApi } from "./api"
import type { AttributePayload, PlayerPayload, RolePayload } from "./types"

const ROLES_KEY = ["players", "roles"] as const
const PLAYERS_KEY = ["players", "list"] as const
const ATTRIBUTES_KEY = ["players", "attributes"] as const

const playerKey = (id: number) => ["players", "detail", id] as const
const playerRolesKey = (id: number) => ["players", "detail", id, "roles"] as const
const playerAttributesKey = (id: number) =>
  ["players", "detail", id, "attributes"] as const

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

export function useAttributes() {
  return useQuery({ queryKey: ATTRIBUTES_KEY, queryFn: attributesApi.list })
}

export function useCreateAttribute() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (payload: AttributePayload) => attributesApi.create(payload),
    onSuccess: () =>
      queryClient.invalidateQueries({ queryKey: ATTRIBUTES_KEY }),
  })
}

export function useUpdateAttribute() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ id, payload }: { id: number; payload: AttributePayload }) =>
      attributesApi.update(id, payload),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["players"] }),
  })
}

export function useDeleteAttribute() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (id: number) => attributesApi.remove(id),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["players"] }),
  })
}

export function usePlayerAttributes(playerId: number) {
  return useQuery({
    queryKey: playerAttributesKey(playerId),
    queryFn: () => playersApi.listAttributes(playerId),
  })
}

export function useRatePlayer(playerId: number) {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({
      attributeId,
      value,
    }: {
      attributeId: number
      value: number
    }) =>
      playersApi.rateAttribute(playerId, { attribute_id: attributeId, value }),
    onSuccess: () =>
      queryClient.invalidateQueries({
        queryKey: playerAttributesKey(playerId),
      }),
  })
}

export function useUpdateRating(playerId: number) {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({
      attributeId,
      value,
    }: {
      attributeId: number
      value: number
    }) => playersApi.updateAttribute(playerId, attributeId, { value }),
    onSuccess: () =>
      queryClient.invalidateQueries({
        queryKey: playerAttributesKey(playerId),
      }),
  })
}

export function useRemoveRating(playerId: number) {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (attributeId: number) =>
      playersApi.removeAttribute(playerId, attributeId),
    onSuccess: () =>
      queryClient.invalidateQueries({
        queryKey: playerAttributesKey(playerId),
      }),
  })
}
