## ADDED Requirements

### Requirement: Agregar comentario a tarea
El sistema SHALL permitir agregar comentarios al hilo de una tarea, con trazabilidad de autor y timestamp.

#### Scenario: COORDINADOR comenta en tarea
- **WHEN** un COORDINADOR envía `POST /api/tareas/{id}/comentarios` con texto
- **THEN** el sistema crea ComentarioTarea con autor_id y creado_at automático

#### Scenario: PROFESOR agrega evidencia en comentario
- **WHEN** el PROFESOR asignado comenta "Adjunto planilla con notas"
- **THEN** el sistema registra el comentario en el hilo

### Requirement: Listar comentarios de tarea
El sistema SHALL permitir ver todos los comentarios de una tarea ordenados por fecha.

#### Scenario: Ver hilo de comentarios
- **WHEN** un usuario envía `GET /api/tareas/{id}/comentarios`
- **THEN** devuelve lista de comentarios ordenados por creado_at ASC

#### Scenario: Tarea sin comentarios
- **WHEN** una tarea no tiene comentarios
- **THEN** devuelve lista vacía

### Requirement: Detalle de tarea con comentarios
El sistema SHALL incluir los comentarios al consultar el detalle de una tarea.

#### Scenario: GET /api/tareas/{id} incluye comentarios
- **WHEN** un usuario consulta una tarea con 3 comentarios
- **THEN** la respuesta incluye la tarea y la lista de sus comentarios
