## ADDED Requirements

### Requirement: Logout revoca sesión

El sistema SHALL proveer un endpoint `POST /api/auth/logout` que reciba el refresh_token actual y lo marque como revocado en la BD. El endpoint SHALL requerir autenticación (access token válido).

#### Scenario: Logout exitoso revoca refresh token

- **GIVEN** un usuario autenticado con un refresh_token R1 activo
- **WHEN** se envía POST /api/auth/logout con refresh_token = R1
- **THEN** la respuesta es 200 OK
- **AND** R1 queda marcado como revocado

#### Scenario: Logout no afecta otros refresh tokens del mismo usuario

- **GIVEN** un usuario con dos refresh tokens activos R1 y R2
- **WHEN** se envía POST /api/auth/logout con refresh_token = R1
- **THEN** R1 queda revocado
- **AND** R2 continúa activo

#### Scenario: Logout con token ya revocado

- **GIVEN** un refresh_token R1 ya revocado
- **WHEN** se envía POST /api/auth/logout con refresh_token = R1
- **THEN** la respuesta es 200 OK (idempotente)
