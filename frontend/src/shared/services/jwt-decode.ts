interface JwtPayload {
  sub: string
  tenant_id: string
  roles?: string[]
  exp: number
  [key: string]: unknown
}

export function decodeJwt(token: string): JwtPayload | null {
  try {
    const parts = token.split('.')
    if (parts.length !== 3) return null

    const payload = parts[1]
    const decoded = atob(payload.replace(/-/g, '+').replace(/_/g, '/'))
    const json = JSON.parse(decoded) as JwtPayload

    if (!json.sub || !json.tenant_id) return null

    return json
  } catch {
    return null
  }
}
