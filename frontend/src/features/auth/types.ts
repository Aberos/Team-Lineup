export type LoginPayload = { username: string; password: string }

export type LoginResponse = { token: string }

export type CurrentUser = {
  username: string
  first_name: string
  last_name: string
  email: string
}
