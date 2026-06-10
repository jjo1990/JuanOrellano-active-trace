## ADDED Requirements

### Requirement: Refresh token con rotación

El sistema SHALL implementar refresh token rotation: cada vez que se usa un refresh token para obtener un nuevo par, el refresh token anterior SHALL invalidarse. Un refresh token usado NO SHALL poder reutilizarse.

#### Scenario: Refresh exitoso invalida el token anterior

- **GIVEN** un refresh_token válido R1
- **WHEN** se envía POST /api/auth/refresh con refresh_token = R1
- **THEN** la respuesta es 200 OK
- **AND** incluye un nuevo access_token y un nuevo refresh_token R2
- **AND** R1 queda marcado como revocado en la BD

#### Scenario: Reuso de refresh token (reuse attack) revoca todas las sesiones

- **GIVEN** un refresh_token R1 que YA fue usado (y por tanto revocado)
- **WHEN** se envía POST /api/auth/refresh con refresh_token = R1
- **THEN** la respuesta es 401 Unauthorized
- **AND** TODAS las sesiones activas del usuario quedan revocadas (todos sus refresh tokens se marcan como revocados)

#### Scenario: Refresh con token inválido

- **WHEN** se envía POST /api/auth/refresh con un refresh_token que no existe o está mal formado
- **THEN** la respuesta es 401 Unauthorized

#### Scenario: Refresh con token expirado

- **GIVEN** un refresh_token expirado
- **WHEN** se envía POST /api/auth/refresh con ese token
- **THEN** la respuesta es 401 Unauthorized

### Requirement: JWT access token con claims mínimos

El sistema SHALL emitir access tokens JWT firmados con HS256. Los claims SHALL ser: `sub` (user_id UUID), `tenant_id` (UUID), `roles` (lista de strings), `exp` (timestamp de expiración). NO SHALL incluir permisos en el token.

#### Scenario: Access token contiene claims requeridos

- **GIVEN** un login exitoso
- **WHEN** se decodifica el access_token
- **THEN** el payload contiene: `sub`, `tenant_id`, `roles`, `exp`
- **AND** no contiene permisos ni datos sensibles

#### Scenario: Access token expira en 15 minutos

- **GIVEN** un login exitoso en tiempo T0
- **WHEN** se verifica el access_token en T0+15min
- **THEN** el token está expirado
- **AND** las requests con ese token son rechazadas con 401
