export type Role = { id: number; name: string }

export type RolePayload = { name: string }

export type PlayerListItem = {
  id: number
  name: string
  number: number
}

export type Player = PlayerListItem & {
  birthday: string
  phone: string
  email: string
}

export type PlayerPayload = Omit<Player, "id">

export type PlayerRolePayload = { role_id: number }

export const ATTRIBUTE_VALUE_MIN = 0
export const ATTRIBUTE_VALUE_MAX = 100

export type Attribute = { id: number; name: string }

export type AttributePayload = { name: string }

export type PlayerAttribute = {
  attribute: Attribute
  value: number
}

export type PlayerAttributeCreatePayload = {
  attribute_id: number
  value: number
}

export type PlayerAttributeUpdatePayload = { value: number }
