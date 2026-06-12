## ADDED Requirements

### Requirement: Modelo Comunicacion con datos cifrados

El sistema SHALL persistir comunicaciones en la tabla `comunicacion` con `destinatario` cifrado en reposo mediante AES-256 (via `EncryptedField`), `tenant_id` para aislamiento multi-tenant, y `deleted_at` para soft-delete.

#### Scenario: Crear comunicacion con destinatario cifrado
- **WHEN** se crea una `Comunicacion` con `destinatario = "alumno@email.com"`
- **THEN** el valor se almacena cifrado en la columna `destinatario_encrypted`
- **AND** al leer la entidad, `comunicacion.destinatario` devuelve `"alumno@email.com"` descifrado

#### Scenario: Tenant isolation en consultas
- **WHEN** se consultan comunicaciones del tenant A
- **THEN** solo se devuelven comunicaciones con `tenant_id = A`
- **AND** las comunicaciones de otros tenants no son visibles

### Requirement: Maquina de estados RN-15

El sistema SHALL validar que toda transicion de estado de una `Comunicacion` cumpla con las transiciones legales definidas en RN-15. Cualquier transicion no permitida DEBE lanzar error.

#### Scenario: Transicion valida Pendiente a Enviando
- **WHEN** se intenta cambiar estado de `Pendiente` a `Enviando`
- **THEN** la transicion es aceptada

#### Scenario: Transicion valida Enviando a Enviado
- **WHEN** se intenta cambiar estado de `Enviando` a `Enviado`
- **THEN** la transicion es aceptada

#### Scenario: Transicion valida Enviando a Error
- **WHEN** se intenta cambiar estado de `Enviando` a `Error`
- **THEN** la transicion es aceptada

#### Scenario: Transicion valida Pendiente a Cancelado
- **WHEN** se intenta cambiar estado de `Pendiente` a `Cancelado`
- **THEN** la transicion es aceptada

#### Scenario: Transicion invalida Enviado a Pendiente
- **WHEN** se intenta cambiar estado de `Enviado` a `Pendiente`
- **THEN** la transicion es rechazada con error

#### Scenario: Transicion invalida Cancelado a cualquier otro
- **WHEN** se intenta cambiar estado de `Cancelado` a `Enviando`
- **THEN** la transicion es rechazada con error

#### Scenario: Transicion invalida Error a Enviando
- **WHEN** se intenta cambiar estado de `Error` a `Enviando`
- **THEN** la transicion es rechazada con error

### Requirement: Preview obligatorio de comunicacion (RN-16)

El sistema SHALL proporcionar un endpoint de preview que renderice una plantilla de comunicacion con datos reales del alumno y devuelva asunto + cuerpo renderizado, sin persistir en base de datos.

#### Scenario: Preview con datos reales
- **WHEN** se solicita preview con `template = "Hola {{nombre}}, tu nota en {{materia}} es {{nota_promedio}}"`
- **AND** se proporciona `alumno_id` con `nombre = "Juan Perez"`, `materia = "Programacion I"`, `nota_promedio = 75`
- **THEN** el sistema devuelve asunto renderizado y cuerpo `"Hola Juan Perez, tu nota en Programacion I es 75"`
- **AND** no se crea ningun registro en la tabla `comunicacion`

#### Scenario: Preview no persiste
- **WHEN** se solicitan 5 previews consecutivos
- **THEN** la tabla `comunicacion` sigue sin registros nuevos

### Requirement: Envio masivo con agrupacion por lote

El sistema SHALL permitir el envio masivo de comunicaciones a multiples alumnos, agrupandolas bajo un mismo `lote_id` UUID. Cada comunicacion se crea con estado `Pendiente`.

#### Scenario: Envio masivo crea lote
- **WHEN** se envia comunicacion a 3 alumnos con template `"Recordatorio {{materia}}"`
- **THEN** se crean 3 registros en `comunicacion`, todas con el mismo `lote_id`
- **AND** cada registro tiene `estado = 'Pendiente'`
- **AND** cada registro tiene el `cuerpo` renderizado con los datos del alumno correspondiente

#### Scenario: Lotes diferentes son independientes
- **WHEN** se realizan 2 envios masivos separados
- **THEN** cada envio genera un `lote_id` diferente
- **AND** las comunicaciones de un lote no afectan al otro

### Requirement: Aprobacion de envios masivos (RN-17)

El sistema SHALL requerir aprobacion explicita con permiso `comunicacion:aprobar` para que las comunicaciones de un lote masivo puedan ser procesadas por el worker. Sin aprobacion, el worker NO DEBE consumirlas.

#### Scenario: Aprobacion de lote completo
- **WHEN** un usuario con `comunicacion:aprobar` aprueba un `lote_id`
- **THEN** todas las comunicaciones Pendiente de ese lote quedan disponibles para el worker
- **AND** la auditoria registra `COMUNICACION_ENVIAR` para cada una

#### Scenario: Lote sin aprobacion no se procesa
- **WHEN** el worker consulta comunicaciones Pendiente
- **AND** existe un lote no aprobado
- **THEN** las comunicaciones de ese lote no son retornadas para procesamiento

#### Scenario: Cancelacion de lote
- **WHEN** un usuario con `comunicacion:aprobar` cancela un `lote_id`
- **THEN** todas las comunicaciones Pendiente de ese lote pasan a estado `Cancelado`

#### Scenario: Usuario sin permiso no puede aprobar
- **WHEN** un usuario sin `comunicacion:aprobar` intenta aprobar un lote
- **THEN** el sistema retorna 403 Forbidden

### Requirement: Cancelacion individual de comunicacion

El sistema SHALL permitir cancelar una comunicacion individual en estado `Pendiente`, ya sea por el creador o por un usuario con `comunicacion:aprobar`.

#### Scenario: Cancelacion por creador
- **WHEN** el usuario que creo la comunicacion solicita cancelarla
- **AND** la comunicacion esta en estado `Pendiente`
- **THEN** el estado cambia a `Cancelado`

#### Scenario: No se puede cancelar comunicacion ya enviada
- **WHEN** se intenta cancelar una comunicacion en estado `Enviado`
- **THEN** el sistema retorna error de transicion invalida

### Requirement: Worker asincronico de despacho

El sistema SHALL ejecutar un worker asincronico que consulte periodicamente comunicaciones en estado `Pendiente`, las transicione a `Enviando`, realice el envio (mockeado para MVP), y las marque como `Enviado` o `Error` segun el resultado.

#### Scenario: Worker procesa Pendiente exitosamente
- **WHEN** existe una comunicacion Pendiente lista para procesar
- **AND** el worker la toma
- **THEN** el estado cambia a `Enviando`
- **AND** luego del envio exitoso cambia a `Enviado`
- **AND** `enviado_at` se establece con la fecha/hora actual

#### Scenario: Worker maneja fallo de envio
- **WHEN** el worker procesa una comunicacion
- **AND** el envio mockeado lanza excepcion
- **THEN** el estado cambia a `Error`
- **AND** `enviado_at` queda en NULL

#### Scenario: Worker respeta batch size
- **WHEN** hay 25 comunicaciones Pendiente
- **AND** el worker tiene `batch_size = 10`
- **THEN** el worker procesa solo 10 en cada iteracion
- **AND** las 15 restantes quedan para la siguiente iteracion

### Requirement: Renderizado de plantillas con variables

El sistema SHALL soportar plantillas de comunicacion con variables de sustitucion delimitadas por `{{variable}}`. Las variables soportadas son: `{{nombre}}`, `{{materia}}`, `{{actividades_pendientes}}`, `{{nota_promedio}}`, `{{link_materia}}`.

#### Scenario: Renderizado basico
- **WHEN** template es `"Hola {{nombre}}"` con contexto `{"nombre": "Ana"}`
- **THEN** resultado es `"Hola Ana"`

#### Scenario: Variables no definidas se preservan
- **WHEN** template contiene `"{{variable_no_definida}}"`
- **AND** el contexto no tiene esa clave
- **THEN** el texto `"{{variable_no_definida}}"` se preserva sin modificar

#### Scenario: Multiples ocurrencias
- **WHEN** template es `"{{nombre}}, tu nota es {{nota}}. Saludos, {{nombre}}"`
- **AND** contexto es `{"nombre": "Ana", "nota": "8"}`
- **THEN** resultado es `"Ana, tu nota es 8. Saludos, Ana"`

### Requirement: Endpoints REST con RBAC

El sistema SHALL exponer endpoints REST bajo `/api/comunicaciones/` protegidos con los permisos `comunicacion:enviar` y `comunicacion:aprobar` segun corresponda.

#### Scenario: Acceso con permiso comunicacion:enviar
- **WHEN** usuario autenticado con permiso `comunicacion:enviar` accede a `POST /api/comunicaciones/preview`
- **THEN** la peticion se procesa normalmente

#### Scenario: Acceso sin permiso
- **WHEN** usuario autenticado sin `comunicacion:enviar` accede a `POST /api/comunicaciones/enviar`
- **THEN** el sistema retorna 403 Forbidden

#### Scenario: Aprobacion requiere permiso especifico
- **WHEN** usuario con `comunicacion:enviar` pero sin `comunicacion:aprobar` accede a `POST /api/comunicaciones/aprobar/{lote_id}`
- **THEN** el sistema retorna 403 Forbidden

### Requirement: Auditoria de comunicaciones

El sistema SHALL registrar en el audit log cada accion de envio de comunicacion con el codigo `COMUNICACION_ENVIAR`.

#### Scenario: Auditoria al enviar
- **WHEN** se ejecuta `POST /api/comunicaciones/enviar` exitosamente
- **THEN** se registra una entrada en `audit_log` con `action_code = 'COMUNICACION_ENVIAR'`
- **AND** el `actor_id` es el usuario que realizo el envio

### Requirement: Consulta de estado de comunicaciones

El sistema SHALL permitir consultar el estado de las comunicaciones por lote y por materia, con filtro opcional por estado.

#### Scenario: Estado de lote
- **WHEN** se consulta `GET /api/comunicaciones/lote/{lote_id}`
- **THEN** se devuelven todas las comunicaciones de ese lote con su estado actual

#### Scenario: Comunicaciones por materia
- **WHEN** se consulta `GET /api/comunicaciones/materia/{materia_id}`
- **THEN** se devuelven todas las comunicaciones de esa materia, filtradas por tenant
- **AND** se puede filtrar opcionalmente con `?estado=Enviado`
