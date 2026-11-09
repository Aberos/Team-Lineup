import { apiRequest } from "@/lib/api-client"

import type {
  Attribute,
  AttributePayload,
  Player,
  PlayerAttribute,
  PlayerAttributeCreatePayload,
  PlayerAttributeUpdatePayload,
  Page,
  PlayerCard,
  PlayerListParams,
  PlayerPayload,
  PlayerRoleItem,
  PlayerRolePayload,
  Role,
  RolePayload,
} from "./types"

const ROLE_PATH = "/role/"
const PLAYER_PATH = "/player/"
const ATTRIBUTE_PATH = "/attribute/"

const playerUrl = (id: number) => `${PLAYER_PATH}${id}/`

function playerListQuery({
  search,
  role,
  ordering,
  page,
  pageSize,
}: PlayerListParams): string {
  const params = new URLSearchParams()
  if (search) {
    params.set("search", search)
  }
  if (role !== undefined && role !== null) {
    params.set("role", String(role))
  }
  if (ordering) {
    params.set("ordering", ordering)
  }
  if (page !== undefined) {
    params.set("page", String(page))
  }
  if (pageSize !== undefined) {
    params.set("page_size", String(pageSize))
  }
  const query = params.toString()
  return query ? `?${query}` : ""
}

export const rolesApi = {
  list: () => apiRequest<Role[]>(ROLE_PATH),
  create: (payload: RolePayload) =>
    apiRequest<Role>(ROLE_PATH, { method: "POST", body: payload }),
  update: (id: number, payload: RolePayload) =>
    apiRequest<Role>(`${ROLE_PATH}${id}/`, { method: "PUT", body: payload }),
  remove: (id: number) =>
    apiRequest<null>(`${ROLE_PATH}${id}/`, { method: "DELETE" }),
}

export const playersApi = {
  list: (params: PlayerListParams = {}) =>
    apiRequest<Page<PlayerCard>>(`${PLAYER_PATH}${playerListQuery(params)}`),
  get: (id: number) => apiRequest<Player>(playerUrl(id)),
  create: (payload: PlayerPayload) =>
    apiRequest<Player>(PLAYER_PATH, { method: "POST", body: payload }),
  update: (id: number, payload: PlayerPayload) =>
    apiRequest<Player>(playerUrl(id), { method: "PUT", body: payload }),
  remove: (id: number) =>
    apiRequest<null>(playerUrl(id), { method: "DELETE" }),
  uploadPhoto: (id: number, photo: File) => {
    const body = new FormData()
    body.append("photo", photo)
    return apiRequest<Player>(`${playerUrl(id)}photo/`, {
      method: "PUT",
      body,
    })
  },
  removePhoto: (id: number) =>
    apiRequest<Player>(`${playerUrl(id)}photo/`, { method: "DELETE" }),
  listRoles: (id: number) =>
    apiRequest<PlayerRoleItem[]>(`${playerUrl(id)}role/`),
  assignRole: (id: number, payload: PlayerRolePayload) =>
    apiRequest<PlayerRoleItem>(`${playerUrl(id)}role/`, {
      method: "POST",
      body: payload,
    }),
  setPrimaryRole: (id: number, roleId: number) =>
    apiRequest<PlayerRoleItem>(`${playerUrl(id)}role/${roleId}/`, {
      method: "PATCH",
      body: { is_primary: true },
    }),
  removeRole: (id: number, roleId: number) =>
    apiRequest<null>(`${playerUrl(id)}role/${roleId}/`, { method: "DELETE" }),
  listAttributes: (id: number) =>
    apiRequest<PlayerAttribute[]>(`${playerUrl(id)}attribute/`),
  rateAttribute: (id: number, payload: PlayerAttributeCreatePayload) =>
    apiRequest<PlayerAttribute>(`${playerUrl(id)}attribute/`, {
      method: "POST",
      body: payload,
    }),
  updateAttribute: (
    id: number,
    attributeId: number,
    payload: PlayerAttributeUpdatePayload,
  ) =>
    apiRequest<PlayerAttribute>(`${playerUrl(id)}attribute/${attributeId}/`, {
      method: "PUT",
      body: payload,
    }),
  removeAttribute: (id: number, attributeId: number) =>
    apiRequest<null>(`${playerUrl(id)}attribute/${attributeId}/`, {
      method: "DELETE",
    }),
}

export const attributesApi = {
  list: () => apiRequest<Attribute[]>(ATTRIBUTE_PATH),
  create: (payload: AttributePayload) =>
    apiRequest<Attribute>(ATTRIBUTE_PATH, { method: "POST", body: payload }),
  update: (id: number, payload: AttributePayload) =>
    apiRequest<Attribute>(`${ATTRIBUTE_PATH}${id}/`, {
      method: "PUT",
      body: payload,
    }),
  remove: (id: number) =>
    apiRequest<null>(`${ATTRIBUTE_PATH}${id}/`, { method: "DELETE" }),
}
