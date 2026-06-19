## ADDED Requirements

### Requirement: Usuario autenticado puede listar sus hilos de mensajes recibidos

El sistema SHALL permitir a cualquier usuario autenticado listar los hilos de mensajes donde es destinatario. Cada hilo se representa por su mensaje raíz con metadata adicional: cantidad de respuestas y fecha de la última respuesta.

#### Scenario: Listado de hilos recibidos

- **WHEN** un usuario autenticado realiza `GET /api/inbox`
- **THEN** el sistema retorna 200 con una lista de hilos donde el usuario es `destinatario_id`. Cada entrada incluye: id del mensaje raíz, remitente (id, nombre, apellidos), asunto, cuerpo (truncado si es muy largo), fecha, cantidad de respuestas, estado de lectura, y fecha de la última respuesta si existe.

#### Scenario: Bandeja vacía

- **WHEN** un usuario autenticado realiza `GET /api/inbox` y no tiene mensajes recibidos
- **THEN** el sistema retorna 200 con una lista vacía `[]`

#### Scenario: Usuario no autenticado accede al inbox

- **WHEN** una petición sin token JWT válido realiza `GET /api/inbox`
- **THEN** el sistema retorna 401 Unauthorized

### Requirement: Usuario puede leer un hilo de mensajes completo

El sistema SHALL permitir al usuario autenticado leer un hilo de mensajes completo (mensaje raíz + todas las respuestas) siempre que sea el destinatario del mensaje raíz o el remitente de alguna respuesta.

#### Scenario: Lectura de hilo como destinatario

- **WHEN** un usuario autenticado realiza `GET /api/inbox/{id}` siendo el destinatario del mensaje raíz
- **THEN** el sistema retorna 200 con el mensaje raíz y todas sus respuestas ordenadas cronológicamente (created_at ascendente). El mensaje raíz se marca como `leido = true`.

#### Scenario: Lectura de hilo como participante (remitente de respuesta)

- **WHEN** un usuario autenticado realiza `GET /api/inbox/{id}` siendo el remitente de al menos una respuesta en el hilo
- **THEN** el sistema retorna 200 con el hilo completo

#### Scenario: Lectura de hilo sin permisos

- **WHEN** un usuario autenticado realiza `GET /api/inbox/{id}` sin ser destinatario ni participante del hilo
- **THEN** el sistema retorna 404 Not Found (no se revela la existencia del hilo)

#### Scenario: Hilo inexistente

- **WHEN** un usuario autenticado realiza `GET /api/inbox/{id}` con un ID que no existe en el tenant
- **THEN** el sistema retorna 404 Not Found

### Requirement: Usuario puede crear un nuevo mensaje para otro usuario

El sistema SHALL permitir a cualquier usuario autenticado enviar un mensaje a otro usuario del mismo tenant, creando un nuevo hilo de conversación.

#### Scenario: Envío exitoso de mensaje

- **WHEN** un usuario autenticado envía `POST /api/inbox` con `{"destinatario_id": "<uuid>", "asunto": "Consulta", "cuerpo": "Texto del mensaje"}`
- **THEN** el sistema crea el mensaje con `remitente_id = current_user.id`, `mensaje_padre_id = null`, `leido = false`, y retorna 201 con el mensaje creado

#### Scenario: Destinatario no existe en el tenant

- **WHEN** un usuario autenticado envía `POST /api/inbox` con un `destinatario_id` que no existe o no pertenece al tenant
- **THEN** el sistema retorna 404 Not Found

#### Scenario: Mensaje sin asunto

- **WHEN** un usuario autenticado envía `POST /api/inbox` con `asunto` vacío o ausente
- **THEN** el sistema retorna 422 Unprocessable Entity

#### Scenario: Mensaje sin cuerpo

- **WHEN** un usuario autenticado envía `POST /api/inbox` con `cuerpo` vacío o ausente
- **THEN** el sistema retorna 422 Unprocessable Entity

### Requirement: Usuario puede responder a un mensaje dentro del hilo

El sistema SHALL permitir al usuario autenticado responder a un mensaje dentro de un hilo existente, siempre que sea el destinatario del mensaje raíz o participante del hilo.

#### Scenario: Respuesta exitosa dentro del hilo

- **WHEN** un usuario autenticado envía `POST /api/inbox/{id}/reply` con `{"cuerpo": "Respuesta al mensaje"}` siendo destinatario del hilo `{id}`
- **THEN** el sistema crea un nuevo mensaje con `remitente_id = current_user.id`, `destinatario_id = remitente del mensaje raíz`, `mensaje_padre_id = {id}`, y retorna 201 con el mensaje creado

#### Scenario: Intento de responder a hilo sin ser participante

- **WHEN** un usuario autenticado envía `POST /api/inbox/{id}/reply` sin ser destinatario ni participante del hilo
- **THEN** el sistema retorna 404 Not Found

#### Scenario: Respuesta sin cuerpo

- **WHEN** un usuario autenticado envía `POST /api/inbox/{id}/reply` con `cuerpo` vacío o ausente
- **THEN** el sistema retorna 422 Unprocessable Entity

### Requirement: Mensajes están aislados por tenant

El sistema SHALL garantizar que los mensajes solo sean visibles dentro del tenant al que pertenecen. Un usuario no puede ver, crear ni responder mensajes de otro tenant.

#### Scenario: Intento de acceder a mensaje de otro tenant

- **WHEN** un usuario del tenant A intenta `GET /api/inbox/{id}` donde `{id}` pertenece al tenant B
- **THEN** el sistema retorna 404 Not Found (el repositorio filtra por tenant_id)

#### Scenario: Intento de enviar mensaje a usuario de otro tenant

- **WHEN** un usuario del tenant A intenta `POST /api/inbox` con un `destinatario_id` que pertenece al tenant B
- **THEN** el sistema retorna 404 Not Found
