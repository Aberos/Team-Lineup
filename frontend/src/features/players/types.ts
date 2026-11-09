export type Role = { id: number; name: string }

export type RolePayload = { name: string }

export type PlayerRoleItem = Role & { is_primary: boolean }

export type CardAttribute = {
  abbreviation: string
  name: string
  value: number | null
}

export type PlayerCard = {
  id: number
  name: string
  number: number
  overall: number | null
  photo_url: string | null
  roles: PlayerRoleItem[]
  card_attributes: CardAttribute[]
}

export type Page<T> = {
  count: number
  page: number
  page_size: number
  next: string | null
  previous: string | null
  results: T[]
}

export const PLAYER_ORDERINGS = {
  name: "Nome (A–Z)",
  "-name": "Nome (Z–A)",
  "-overall": "Maior nota geral",
  overall: "Menor nota geral",
} as const

export type PlayerOrdering = keyof typeof PLAYER_ORDERINGS

export type PlayerListParams = {
  search?: string
  role?: number | null
  ordering?: PlayerOrdering
  page?: number
  pageSize?: number
}

export type Player = {
  id: number
  name: string
  number: number
  birthday: string
  phone: string
  email: string
  overall: number | null
  photo_url: string | null
}

export type PlayerPayload = Pick<
  Player,
  "name" | "number" | "birthday" | "phone" | "email"
>

export type PlayerRolePayload = { role_id: number }

export const ATTRIBUTE_VALUE_MIN = 0
export const ATTRIBUTE_VALUE_MAX = 100
export const CARD_SLOTS = [1, 2, 3, 4, 5, 6] as const

export type Attribute = {
  id: number
  name: string
  abbreviation: string
  card_order: number | null
}

export type AttributePayload = Omit<Attribute, "id">

export type PlayerAttribute = {
  attribute: Attribute
  value: number
}

export type PlayerAttributeCreatePayload = {
  attribute_id: number
  value: number
}

export type PlayerAttributeUpdatePayload = { value: number }
