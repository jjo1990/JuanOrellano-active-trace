## ADDED Requirements

### Requirement: AES-256-GCM encryption utility

El sistema SHALL proveer una utilidad de cifrado simétrico utilizando AES-256 en modo GCM (Galois/Counter). La clave SHALL tener exactamente 32 bytes (256 bits) y SHALL obtenerse de la variable de entorno `ENCRYPTION_KEY`.

#### Scenario: Encrypt produce ciphertext con nonce y tag

- **WHEN** se cifra un texto plano con una clave válida
- **THEN** el resultado es un string en base64
- **AND** el string contiene el nonce (12 bytes), el ciphertext y el tag de autenticación (16 bytes)
- **AND** el resultado no es igual al texto plano original

#### Scenario: Decrypt recupera el texto original

- **GIVEN** un texto plano cifrado con encrypt()
- **WHEN** se ejecuta decrypt() con el mismo ciphertext y la misma clave
- **THEN** el resultado es el texto plano original

### Requirement: Clave de 32 bytes obligatoria

El sistema SHALL validar que `ENCRYPTION_KEY` tenga exactamente 32 bytes antes de realizar cualquier operación de cifrado. Si la clave tiene otra longitud, SHALL lanzar un error.

#### Scenario: Clave inválida es rechazada

- **GIVEN** una clave de 16 bytes
- **WHEN** se intenta inicializar la utilidad de cifrado
- **THEN** se lanza un error indicando que la clave debe tener 32 bytes

### Requirement: Nonce aleatorio por operación

Cada llamada a `encrypt` SHALL generar un nonce aleatorio nuevo de 12 bytes usando un generador criptográficamente seguro.

#### Scenario: Nonces diferentes

- **WHEN** se cifra el mismo texto plano dos veces con la misma clave
- **THEN** los dos ciphertext resultantes son distintos entre sí (debido a nonces diferentes)

### Requirement: Ciphertext corrupto es detectado

Si el ciphertext, nonce o tag se modifican, el decrypt SHALL fallar con un error de autenticación.

#### Scenario: Tag inválido

- **GIVEN** un ciphertext válido
- **WHEN** se modifica cualquier byte del ciphertext antes de llamar a decrypt
- **THEN** la operación decrypt falla con un error de desencriptación/autenticación
