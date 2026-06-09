## ADDED Requirements

### Requirement: Modelo User con email único por tenant

El sistema SHALL modelar un Usuario como entidad asociada a un Tenant. Cada usuario SHALL tener un email único dentro de su tenant (no necesariamente global). El tenant_id SHALL ser obligatorio (FK → tenant.id).

#### Scenario: Creación de usuario con email único en el tenant

- **GIVEN** un tenant existente
- **AND** no existe otro usuario con email "user@example.com" en ese tenant
- **WHEN** se crea un usuario con email "user@example.com" en ese tenant
- **THEN** el usuario se guarda con UUID único
- **AND** su email es "user@example.com"
- **AND** su tenant_id es el UUID del tenant

#### Scenario: Email duplicado en el mismo tenant es rechazado

- **GIVEN** un tenant con un usuario existente de email "user@example.com"
- **WHEN** se intenta crear otro usuario con el mismo email en el mismo tenant
- **THEN** la operación falla con un error de unicidad

#### Scenario: Mismo email en distintos tenants es válido

- **GIVEN** un usuario con email "user@example.com" en tenant A
- **WHEN** se crea un usuario con email "user@example.com" en tenant B
- **THEN** la creación es exitosa
- **AND** ambos usuarios existen con el mismo email pero distinto tenant_id

### Requirement: Password hasheado con Argon2id

El sistema SHALL almacenar las contraseñas de los usuarios hasheadas con Argon2id. Nunca SHALL almacenar una contraseña en texto plano, ni con algoritmos débiles (MD5, SHA-1, SHA-256 simple sin salt).

#### Scenario: Password se almacena hasheado

- **GIVEN** un usuario nuevo con password "securePass123!"
- **WHEN** se guarda el usuario
- **THEN** el campo password contiene un hash de Argon2id
- **AND** el hash es diferente del password original

#### Scenario: Verificación de password correcto

- **GIVEN** un usuario existente con password "securePass123!"
- **WHEN** se verifica el password "securePass123!" contra el hash almacenado
- **THEN** la verificación retorna éxito

#### Scenario: Verificación de password incorrecto

- **GIVEN** un usuario existente con password "securePass123!"
- **WHEN** se verifica el password "wrongPassword" contra el hash almacenado
- **THEN** la verificación retorna fallo

### Requirement: Soft delete en User

User SHALL soportar soft delete a través del campo `deleted_at` heredado de BaseModelMixin.

#### Scenario: Soft delete de usuario

- **GIVEN** un usuario activo
- **WHEN** se ejecuta soft delete sobre ese usuario
- **THEN** `deleted_at` se establece al momento actual
- **AND** el registro continúa existiendo en la base de datos
- **AND** el usuario no puede iniciar sesión

### Requirement: 2FA secret cifrado en reposo

El campo `totp_secret` del usuario SHALL almacenarse cifrado con AES-256-GCM. Nunca SHALL almacenarse en texto plano.

#### Scenario: 2FA secret se almacena cifrado

- **GIVEN** un usuario que enrolla 2FA con un secret TOTP
- **WHEN** se guarda el secret en el usuario
- **THEN** el valor almacenado en `totp_secret` es texto cifrado (diferente del secret original)
- **AND** puede descifrarse correctamente para verificar tokens TOTP
