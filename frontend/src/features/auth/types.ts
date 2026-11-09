export type LoginPayload = { username: string; password: string }

export type LoginResponse = { token: string; refresh: string }

export type CurrentUser = {
  username: string
  first_name: string
  last_name: string
  email: string
  is_staff: boolean
}
