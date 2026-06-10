## ADDED Requirements

### Requirement: Solicitar recuperación de contraseña

El sistema SHALL proveer un endpoint `POST /api/auth/forgot` que reciba un email, genere un token de un solo uso con expiración corta (30 minutos) y lo almacene en la BD hasheado. El endpoint SHALL responder siempre 200 OK para no revelar si el email existe o no.

#### Scenario: Solicitud de recuperación para email existente

- **GIVEN** un usuario con email "user@example.com"
- **WHEN** se envía POST /api/auth/forgot con email="user@example.com"
- **THEN** la respuesta es 200 OK
- **AND** se genera un password_reset_token asociado al usuario
- **AND** el token tiene expiración de 30 minutos
- **AND** el token se almacena hasheado (SHA-256) en la BD
- **AND** se dispara el envío de email con el token raw

#### Scenario: Solicitud de recuperación para email inexistente

- **WHEN** se envía POST /api/auth/forgot con email="noexiste@example.com"
- **THEN** la respuesta es 200 OK (misma respuesta que email existente)
- **AND** no se genera ningún token

### Requirement: Resetear contraseña con token

El sistema SHALL proveer un endpoint `POST /api/auth/reset` que reciba un token (raw) y un nuevo password. Si el token es válido (existe, no expirado, no usado), SHALL actualizar el password y marcar el token como usado. El token SHALL ser de UN solo uso.

#### Scenario: Reset exitoso con token válido

- **GIVEN** un password_reset_token válido (no expirado, no usado) asociado a un usuario
- **WHEN** se envía POST /api/auth/reset con el token raw y un nuevo password "newPass456!"
- **THEN** la respuesta es 200 OK
- **AND** el password del usuario se actualiza a "newPass456!"
- **AND** el token se marca como usado

#### Scenario: Reset con token ya usado

- **GIVEN** un password_reset_token que ya fue marcado como usado
- **WHEN** se envía POST /api/auth/reset con ese token y cualquier password
- **THEN** la respuesta es 400 Bad Request
- **AND** el password no se modifica

#### Scenario: Reset con token expirado

- **GIVEN** un password_reset_token con expiración >30 minutos en el pasado
- **WHEN** se envía POST /api/auth/reset con ese token y cualquier password
- **THEN** la respuesta es 400 Bad Request
- **AND** el password no se modifica

#### Scenario: Reset con token inválido (mal formado)

- **WHEN** se envía POST /api/auth/reset con un token raw que no corresponde a ningún hash en BD
- **THEN** la respuesta es 400 Bad Request
