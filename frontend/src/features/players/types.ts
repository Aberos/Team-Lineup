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
