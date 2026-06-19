## ADDED Requirements

### Requirement: Registrar guardia
El sistema SHALL permitir a un TUTOR con permiso `guardias:registrar` registrar una guardia cubierta (F6.6).

#### Scenario: Registro exitoso de guardia
- **WHEN** un TUTOR envía `POST /api/guardias` con `materia_id`, `carrera_id`, `cohorte_id`, `asignacion_id`, `dia=Lunes`, `horario=14:00–14:45` y `estado=Realizada`
- **THEN** el sistema crea el registro de guardia con `creada_at` automático y asociado al tenant del usuario

#### Scenario: TUTOR registra guardia para su propia asignación
- **WHEN** un TUTOR registra una guardia con un `asignacion_id` que le pertenece
- **THEN** el sistema permite la operación

#### Scenario: TUTOR registra guardia con asignación de otro
- **WHEN** un TUTOR intenta registrar una guardia con un `asignacion_id` de otro usuario
- **THEN** el sistema rechaza con 403

#### Scenario: Usuario sin permiso intenta registrar guardia
- **WHEN** un ALUMNO envía `POST /api/guardias`
- **THEN** el sistema responde con 403 Forbidden

### Requirement: Consultar guardias con filtros
El sistema SHALL permitir consultar guardias con filtros por materia, carrera, cohorte, estado y rango de fechas.

#### Scenario: COORDINADOR consulta todas las guardias
- **WHEN** un COORDINADOR envía `GET /api/guardias`
- **THEN** el sistema devuelve todas las guardias del tenant

#### Scenario: Filtrar guardias por materia
- **WHEN** un usuario envía `GET /api/guardias?materia_id={id}`
- **THEN** el sistema devuelve solo las guardias de esa materia

#### Scenario: Filtrar guardias por estado
- **WHEN** un usuario envía `GET /api/guardias?estado=Realizada`
- **THEN** el sistema devuelve solo las guardias con estado Realizada

#### Scenario: TUTOR consulta solo sus guardias
- **WHEN** un TUTOR envía `GET /api/guardias`
- **THEN** el sistema devuelve solo las guardias registradas por ese TUTOR (scope propio)

### Requirement: Editar guardia
El sistema SHALL permitir modificar el estado, horario y comentarios de una guardia existente.

#### Scenario: Cambiar estado de guardia a Cancelada
- **WHEN** un TUTOR envía `PUT /api/guardias/{id}` con `estado=Cancelada` y `comentarios=Alumno no se presentó`
- **THEN** el sistema actualiza el estado y comentarios de la guardia

#### Scenario: Editar guardia de otro TUTOR
- **WHEN** un TUTOR intenta editar una guardia registrada por otro TUTOR
- **THEN** el sistema rechaza con 403 (a menos que sea COORDINADOR o ADMIN)

### Requirement: Exportar guardias a CSV
El sistema SHALL permitir exportar el registro de guardias en formato CSV.

#### Scenario: Exportación exitosa de guardias
- **WHEN** un COORDINADOR envía `GET /api/guardias/exportar?materia_id={id}`
- **THEN** el sistema devuelve un archivo CSV con columnas: Materia, Carrera, Cohorte, Tutor, Día, Horario, Estado, Comentarios, Fecha de registro

#### Scenario: Exportación sin resultados
- **WHEN** un COORDINADOR envía `GET /api/guardias/exportar` y no hay guardias que coincidan con los filtros
- **THEN** el sistema devuelve CSV con solo la fila de encabezados

### Requirement: Soft delete en guardias
El sistema SHALL implementar soft delete para guardias. Las guardias eliminadas no aparecen en listados ni exportaciones.

#### Scenario: Eliminar guardia (soft delete)
- **WHEN** un COORDINADOR envía `DELETE /api/guardias/{id}`
- **THEN** el sistema establece `deleted_at` en la guardia

#### Scenario: Guardia eliminada no aparece en listado
- **WHEN** un usuario lista guardias después de que una fue soft-deleteada
- **THEN** la guardia eliminada no aparece en el resultado

### Requirement: Aislamiento multi-tenant en guardias
El sistema SHALL aislar las guardias por tenant.

#### Scenario: Usuario de tenant A consulta guardia de tenant B
- **WHEN** un usuario del tenant A envía `GET /api/guardias` con un `materia_id` del tenant B
- **THEN** el sistema devuelve resultados vacíos (no revela datos de otro tenant)
