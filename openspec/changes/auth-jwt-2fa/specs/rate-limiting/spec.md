## ADDED Requirements

### Requirement: Rate limiting en login

El sistema SHALL limitar los intentos de login a 5 por ventana de 60 segundos por combinación de IP + email. Superado el límite, SHALL rechazar el intento con 429 Too Many Requests.

#### Scenario: 5 intentos fallidos en 60 segundos bloquean el login

- **GIVEN** una IP con 5 intentos de login fallidos para email "user@example.com" en los últimos 60 segundos
- **WHEN** se envía un 6to intento POST /api/auth/login con email="user@example.com" desde la misma IP
- **THEN** la respuesta es 429 Too Many Requests
- **AND** el intento no se procesa (no se valida la contraseña)

#### Scenario: Rate limit se resetea después de 60 segundos

- **GIVEN** una IP con 5 intentos fallidos para email "user@example.com"
- **WHEN** pasan 60 segundos
- **AND** se envía un nuevo intento POST /api/auth/login con email="user@example.com" desde la misma IP
- **THEN** la respuesta es 200 o 401 (se procesa normalmente, no es 429)

#### Scenario: Rate limit es por IP+email (no global)

- **GIVEN** una IP con 5 intentos fallidos para email "alice@example.com"
- **WHEN** se envía POST /api/auth/login con email="bob@example.com" desde la misma IP
- **THEN** la respuesta es 200 o 401 (no es 429, el rate limit es diferente para bob@example.com)

#### Scenario: Login exitoso resetea el contador de rate limit

- **GIVEN** una IP con 4 intentos fallidos para email "user@example.com"
- **WHEN** se envía POST /api/auth/login con credenciales correctas
- **THEN** la respuesta es 200 OK (login exitoso)
- **AND** el contador de rate limit para esa IP+email se resetea

#### Scenario: Rate limit no afecta otros endpoints

- **GIVEN** una IP bloqueada para login (429)
- **WHEN** se envía POST /api/auth/forgot desde la misma IP
- **THEN** la respuesta NO es 429 (el rate limit solo aplica a login)
