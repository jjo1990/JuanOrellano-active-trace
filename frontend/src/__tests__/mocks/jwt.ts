function base64urlEncode(str: string): string {
  return btoa(str).replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '')
}

export interface JwtClaims {
  sub: string
  tenant_id: string
  roles?: string[]
  exp?: number
}

export function createTestToken(claims: JwtClaims): string {
  const header = base64urlEncode(JSON.stringify({ alg: 'HS256', typ: 'JWT' }))

  const payload = {
    sub: claims.sub,
    tenant_id: claims.tenant_id,
    roles: claims.roles ?? ['PROFESOR'],
    exp: claims.exp ?? Math.floor(Date.now() / 1000) + 3600,
  }

  const payloadEncoded = base64urlEncode(JSON.stringify(payload))
  const signature = base64urlEncode('test-signature')

  return `${header}.${payloadEncoded}.${signature}`
}
