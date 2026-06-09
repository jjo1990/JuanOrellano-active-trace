## ADDED Requirements

### Requirement: Enrollar 2FA TOTP

El sistema SHALL proveer un endpoint `POST /api/auth/2fa/enroll` que genere un secreto TOTP, lo devuelva al usuario (junto con la URI para QR) y lo almacene cifrado en la cuenta del usuario. El 2FA NO SHALL activarse hasta que se verifique un primer TOTP exitoso.

#### Scenario: Enroll exitoso

- **GIVEN** un usuario autenticado sin 2FA habilitado
- **WHEN** se envía POST /api/auth/2fa/enroll
- **THEN** la respuesta es 200 OK
- **AND** incluye `secret` (base32) y `uri` (formato `otpauth://totp/...`)
- **AND** el secret se almacena cifrado en la cuenta del usuario
- **AND** el 2FA del usuario NO está habilitado todavía (pending verification)

### Requirement: Verificar y activar 2FA TOTP

El sistema SHALL proveer un endpoint `POST /api/auth/2fa/verify` que reciba un código TOTP, lo verifique contra el secret almacenado y active el 2FA para el usuario.

#### Scenario: Verificación exitosa activa 2FA

- **GIVEN** un usuario con secret TOTP almacenado pero 2FA no activado
- **WHEN** se envía POST /api/auth/2fa/verify con un TOTP válido
- **THEN** la respuesta es 200 OK
- **AND** el 2FA del usuario queda habilitado

#### Scenario: Verificación con TOTP inválido no activa 2FA

- **GIVEN** un usuario con secret TOTP almacenado pero 2FA no activado
- **WHEN** se envía POST /api/auth/2fa/verify con un TOTP inválido
- **THEN** la respuesta es 400 Bad Request
- **AND** el 2FA del usuario NO se activa

### Requirement: Consultar estado de 2FA

El sistema SHALL proveer un endpoint `GET /api/auth/2fa/status` que indique si el usuario tiene 2FA habilitado.

#### Scenario: Usuario sin 2FA

- **GIVEN** un usuario autenticado sin 2FA habilitado
- **WHEN** se envía GET /api/auth/2fa/status
- **THEN** la respuesta es 200 OK con `enabled: false`

#### Scenario: Usuario con 2FA

- **GIVEN** un usuario autenticado con 2FA habilitado
- **WHEN** se envía GET /api/auth/2fa/status
- **THEN** la respuesta es 200 OK con `enabled: true`
