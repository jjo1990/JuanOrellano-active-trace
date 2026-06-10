## ADDED Requirements

### Requirement: Permiso impersonacion:usar
El sistema SHALL incluir el permiso `impersonacion:usar` en el módulo `auth`. Este permiso SHALL estar asignado al rol ADMIN y al rol COORDINADOR en la matriz de permisos.

#### Scenario: Permiso existe en catálogo
- **WHEN** se consulta la tabla `permiso` por el código `impersonacion:usar`
- **THEN** existe un registro con modulo `auth` y descripción "Suplantar a otro usuario para diagnóstico"

#### Scenario: ADMIN puede impersonar
- **WHEN** un usuario con rol ADMIN intenta impersonar a otro usuario
- **THEN** el sistema verifica el permiso `impersonacion:usar` y permite la operación

#### Scenario: COORDINADOR puede impersonar
- **WHEN** un usuario con rol COORDINADOR intenta impersonar a otro usuario
- **THEN** el sistema verifica el permiso `impersonacion:usar` y permite la operación

### Requirement: Inicio de impersonación
El sistema SHALL exponer un endpoint `POST /auth/impersonate/{user_id}` que permita a un usuario autorizado (con `impersonacion:usar`) iniciar una sesión de impersonación sobre otro usuario.

#### Scenario: Iniciar impersonación exitosa
- **WHEN** un usuario autenticado con permiso `impersonacion:usar` envía `POST /auth/impersonate/{target_user_id}`
- **THEN** el sistema registra la acción `IMPERSONACION_INICIAR` en el audit log con `actor_id` = usuario real y `impersonado_id` = target user
- **THEN** el sistema retorna un token JWT que identifica la sesión como impersonación
- **THEN** el request context marca `request.state.impersonating = target_user_id`

#### Scenario: Iniciar impersonación sin permiso
- **WHEN** un usuario SIN permiso `impersonacion:usar` envía `POST /auth/impersonate/{user_id}`
- **THEN** el sistema devuelve HTTP 403 Forbidden

#### Scenario: Iniciar impersonación sobre usuario inexistente
- **WHEN** un usuario envía `POST /auth/impersonate/{inexistent_user_id}`
- **THEN** el sistema devuelve HTTP 404 Not Found

### Requirement: Finalización de impersonación
El sistema SHALL exponer un endpoint `POST /auth/impersonate/stop` que finalice la impersonación activa y restaure la sesión original.

#### Scenario: Finalizar impersonación exitosa
- **WHEN** un usuario con impersonación activa envía `POST /auth/impersonate/stop`
- **THEN** el sistema registra la acción `IMPERSONACION_FINALIZAR` en el audit log con `actor_id` = usuario real y `impersonado_id` = usuario impersonado
- **THEN** el sistema restaura el token JWT original del actor real
- **THEN** `request.state.impersonating` se establece a `None`

#### Scenario: Finalizar sin impersonación activa
- **WHEN** un usuario SIN impersonación activa envía `POST /auth/impersonate/stop`
- **THEN** el sistema devuelve HTTP 400 Bad Request con mensaje "No hay impersonación activa"

### Requirement: Atribución de acciones bajo impersonación
Toda acción realizada durante una sesión de impersonación SHALL quedar registrada en el audit log con `actor_id` = usuario real (quien impersona) y `impersonado_id` = usuario impersonado (en cuyo nombre se actúa).

#### Scenario: Acción durante impersonación
- **WHEN** un usuario impersonando a otro ejecuta una acción que genera audit log (ej: importar calificaciones)
- **THEN** el registro de auditoría tiene `actor_id` = ID del usuario real y `impersonado_id` = ID del usuario impersonado

#### Scenario: Acción sin impersonación
- **WHEN** un usuario SIN impersonación activa ejecuta una acción que genera audit log
- **THEN** el registro de auditoría tiene `actor_id` = ID del usuario y `impersonado_id` = NULL

### Requirement: Sesión distinguible
El sistema SHALL marcar las sesiones de impersonación como distinguibles de las sesiones normales, tanto en el JWT como en el audit log.

#### Scenario: JWT de impersonación tiene flag
- **WHEN** se inicia una impersonación
- **THEN** el JWT emitido incluye un claim `impersonating: true` además del `actor_id` original
