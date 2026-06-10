## ADDED Requirements

### Requirement: get_current_user dependency

El sistema SHALL proveer una dependency FastAPI `get_current_user` que resuelva la identidad del usuario autenticado desde el JWT access token. Esta dependency SHALL verificar la firma, expiración y extraer `user_id`, `tenant_id` y `roles` del token.

#### Scenario: Token válido resuelve usuario

- **GIVEN** un access_token JWT válido con claims `sub`, `tenant_id`, `roles`
- **WHEN** se inyecta `get_current_user` en un endpoint protegido
- **THEN** retorna un objeto con `user_id`, `tenant_id` y `roles` extraídos del token

#### Scenario: Token expirado es rechazado

- **GIVEN** un access_token JWT expirado
- **WHEN** se inyecta `get_current_user`
- **THEN** la dependency lanza HTTPException 401

#### Scenario: Token con firma inválida es rechazado

- **GIVEN** un token JWT con firma inválida
- **WHEN** se inyecta `get_current_user`
- **THEN** la dependency lanza HTTPException 401

#### Scenario: Token sin claims requeridos es rechazado

- **GIVEN** un token JWT válido pero sin claim `sub`
- **WHEN** se inyecta `get_current_user`
- **THEN** la dependency lanza HTTPException 401

### Requirement: get_tenant_from_jwt dependency

El sistema SHALL proveer una dependency `get_tenant_from_jwt` que resuelva el `tenant_id` desde el JWT verificado. Esta dependency SHALL reemplazar el placeholder `get_tenant` de C-02.

#### Scenario: Tenant ID se resuelve del JWT

- **GIVEN** un access_token con `tenant_id` = UUID_T
- **WHEN** se inyecta `get_tenant_from_jwt`
- **THEN** retorna el UUID_T

#### Scenario: Identidad NO puede ser suplantada por parámetro

- **GIVEN** un usuario autenticado con tenant_id = A
- **WHEN** se envía una request con un parámetro `?tenant_id=B` o header `X-Tenant-ID: B`
- **THEN** el `get_tenant_from_jwt` retorna A (el valor del JWT)
- **AND** el parámetro externo es ignorado

### Requirement: Endpoints protegidos requieren autenticación

Todo endpoint que no sea de auth pública (login, forgot, reset) SHALL requerir autenticación vía `get_current_user`.

#### Scenario: Endpoint protegido sin token

- **WHEN** se accede a un endpoint protegido sin header Authorization
- **THEN** la respuesta es 401 Unauthorized

#### Scenario: Endpoint protegido con token inválido

- **WHEN** se accede a un endpoint protegido con un token inválido
- **THEN** la respuesta es 401 Unauthorized

#### Scenario: Endpoint público es accesible sin token

- **WHEN** se accede a POST /api/auth/login sin token
- **THEN** la respuesta NO es 401 (es 200, 400, o 401 según la validación de credenciales, pero no por falta de token)
