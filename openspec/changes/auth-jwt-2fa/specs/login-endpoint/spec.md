## ADDED Requirements

### Requirement: Login con email y password

El sistema SHALL proveer un endpoint `POST /api/auth/login` que reciba email y password, valide las credenciales contra el registro del tenant correspondiente y emita una sesión JWT si son válidas.

#### Scenario: Login exitoso sin 2FA

- **GIVEN** un usuario activo con email "user@example.com" y password "securePass123!"
- **AND** el usuario NO tiene 2FA habilitado
- **WHEN** se envía POST /api/auth/login con email="user@example.com" y password="securePass123!"
- **THEN** la respuesta es 200 OK
- **AND** incluye un `access_token` (JWT válido por 15 minutos)
- **AND** incluye un `refresh_token` (token opaco, almacenado en BD)
- **AND** incluye `token_type: "bearer"`

#### Scenario: Login con credenciales inválidas

- **GIVEN** un usuario con email "user@example.com" y password "securePass123!"
- **WHEN** se envía POST /api/auth/login con email="user@example.com" y password="wrongPassword"
- **THEN** la respuesta es 401 Unauthorized
- **AND** no se emite ningún token

#### Scenario: Login de usuario inexistente

- **WHEN** se envía POST /api/auth/login con email="noexiste@example.com" y cualquier password
- **THEN** la respuesta es 401 Unauthorized
- **AND** no se revela si el email existe o no (mismo mensaje que credenciales inválidas)

#### Scenario: Login de usuario soft-deleteado

- **GIVEN** un usuario soft-deleteado con email "user@example.com"
- **WHEN** se envía POST /api/auth/login con credenciales correctas
- **THEN** la respuesta es 401 Unauthorized

#### Scenario: Login con 2FA requiere segundo paso

- **GIVEN** un usuario activo con 2FA TOTP habilitado
- **WHEN** se envía POST /api/auth/login con credenciales correctas
- **THEN** la respuesta es 200 OK
- **AND** incluye `requires_2fa: true`
- **AND** incluye un `challenge_token` (JWT parcial, válido 5 minutos, solo para completar 2FA)
- **AND** NO incluye `access_token` ni `refresh_token`

### Requirement: Complete 2FA login

El sistema SHALL proveer un endpoint `POST /api/auth/login/2fa` que reciba un challenge_token y un código TOTP, verifique el código y emita la sesión completa.

#### Scenario: 2FA completion exitoso

- **GIVEN** un challenge_token válido (emitido tras login con credenciales OK + 2FA habilitado)
- **WHEN** se envía POST /api/auth/login/2fa con challenge_token y un TOTP válido
- **THEN** la respuesta es 200 OK
- **AND** incluye `access_token` y `refresh_token`

#### Scenario: 2FA completion con TOTP inválido

- **GIVEN** un challenge_token válido
- **WHEN** se envía POST /api/auth/login/2fa con challenge_token y un TOTP inválido
- **THEN** la respuesta es 401 Unauthorized
- **AND** no se emiten tokens

#### Scenario: 2FA completion con challenge_token expirado

- **GIVEN** un challenge_token expirado (>5 minutos desde emisión)
- **WHEN** se envía POST /api/auth/login/2fa con ese challenge_token y cualquier TOTP
- **THEN** la respuesta es 401 Unauthorized
