export const APP_PREFIX = __APP_PREFIX__

export function withPrefix(path: string): string {
  return `${APP_PREFIX}${path}`
}
