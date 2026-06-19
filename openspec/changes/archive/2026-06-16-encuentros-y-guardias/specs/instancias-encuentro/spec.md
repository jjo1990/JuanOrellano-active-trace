## ADDED Requirements

### Requirement: Crear instancia de encuentro independiente
El sistema SHALL permitir crear una instancia de encuentro que no pertenece a ningún slot (encuentro único ad-hoc, F6.2).

#### Scenario: Creación exitosa de instancia independiente
- **WHEN** un PROFESOR envía `POST /api/encuentros/instancias` con `fecha=2026-05-10`, `hora=14:00`, `titulo=Consulta pre-parcial`, `materia_id` y `asignacion_id` válidos
- **THEN** el sistema crea la instancia con estado Programado y `slot_id=NULL`

#### Scenario: Instancia independiente sin materia_id
- **WHEN** un PROFESOR envía `POST /api/encuentros/instancias` sin `materia_id`
- **THEN** el sistema rechaza con 422 y detalle del campo faltante

### Requirement: Editar instancia de encuentro
El sistema SHALL permitir modificar el estado, meet_url, video_url y comentario de una instancia individual sin afectar al slot padre ni a otras instancias (RN-14, F6.3).

#### Scenario: Marcar instancia como Realizada con grabación
- **WHEN** un PROFESOR envía `PUT /api/encuentros/instancias/{id}` con `estado=Realizado` y `video_url=https://meet.google.com/recording/abc`
- **THEN** el sistema actualiza solo esa instancia; otras instancias del mismo slot mantienen su estado previo

#### Scenario: Cancelar instancia
- **WHEN** un PROFESOR envía `PUT /api/encuentros/instancias/{id}` con `estado=Cancelado` y `comentario=El docente está de licencia`
- **THEN** el sistema actualiza el estado y comentario de la instancia

#### Scenario: Estado inválido
- **WHEN** un PROFESOR envía `PUT /api/encuentros/instancias/{id}` con `estado=Inventado`
- **THEN** el sistema rechaza con 422 indicando que el estado debe ser Programado, Realizado o Cancelado

#### Scenario: Editar instancia de otro docente
- **WHEN** un PROFESOR intenta editar una instancia cuyo slot pertenece a una asignación de otro docente
- **THEN** el sistema rechaza con 403 (a menos que sea COORDINADOR)

### Requirement: Listar instancias por slot
El sistema SHALL permitir listar todas las instancias de un slot, ordenadas por fecha.

#### Scenario: Listado de instancias de un slot recurrente
- **WHEN** un usuario envía `GET /api/encuentros/slots/{id}/instancias` de un slot con 4 instancias
- **THEN** el sistema devuelve la lista de 4 instancias ordenadas por fecha ascendente

### Requirement: Consultar mis encuentros
El sistema SHALL permitir a un usuario autenticado consultar los encuentros de las materias donde tiene asignación vigente.

#### Scenario: PROFESOR consulta sus encuentros
- **WHEN** un PROFESOR envía `GET /api/encuentros/mis-encuentros`
- **THEN** el sistema devuelve todos los slots e instancias asociados a las materias de sus asignaciones vigentes

#### Scenario: Usuario sin asignaciones
- **WHEN** un usuario sin asignaciones envía `GET /api/encuentros/mis-encuentros`
- **THEN** el sistema devuelve lista vacía

### Requirement: Soft delete en instancias
El sistema SHALL implementar soft delete para instancias de encuentro. Las instancias eliminadas no aparecen en listados pero se conservan para auditoría.

#### Scenario: Eliminar instancia (soft delete)
- **WHEN** un COORDINADOR envía `DELETE /api/encuentros/instancias/{id}`
- **THEN** el sistema establece `deleted_at` en la instancia, la cual deja de aparecer en listados

#### Scenario: Instancia eliminada no visible en listado
- **WHEN** un usuario lista instancias de un slot que tiene una instancia con soft delete
- **THEN** la instancia eliminada no aparece en el resultado
