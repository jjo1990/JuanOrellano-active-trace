## ADDED Requirements

### Requirement: Crear slot de encuentro recurrente
El sistema SHALL permitir a un usuario con permiso `encuentros:gestionar` crear un slot de encuentro que genera automáticamente múltiples instancias semanales según RN-13.

#### Scenario: Creación exitosa de slot recurrente
- **WHEN** un PROFESOR envía `POST /api/encuentros/slots` con `dia_semana=Lunes`, `hora=18:00`, `fecha_inicio=2026-03-09`, `cant_semanas=4`, `materia_id` y `asignacion_id` válidos
- **THEN** el sistema crea el slot con 4 instancias en las fechas 2026-03-09, 2026-03-16, 2026-03-23, 2026-03-30, cada una con estado Programado y la misma hora

#### Scenario: Slot recurrente con cant_semanas inválida
- **WHEN** un PROFESOR envía `POST /api/encuentros/slots` con `cant_semanas=0` en modo recurrente
- **THEN** el sistema rechaza con 422 y mensaje indicando que `cant_semanas` debe ser >= 1

#### Scenario: Slot recurrente faltando campos obligatorios
- **WHEN** un PROFESOR envía `POST /api/encuentros/slots` sin `dia_semana` o sin `fecha_inicio`
- **THEN** el sistema rechaza con 422 y detalle de campos faltantes

### Requirement: Crear slot de encuentro único
El sistema SHALL permitir crear un slot que genera una única instancia en una fecha específica (modo único de RN-13).

#### Scenario: Creación exitosa de slot único
- **WHEN** un PROFESOR envía `POST /api/encuentros/slots` con `fecha_unica=2026-04-15`, `hora=10:00`, `materia_id` y `asignacion_id` válidos, sin `cant_semanas` ni `dia_semana`
- **THEN** el sistema crea el slot con 1 instancia en la fecha 2026-04-15 con estado Programado

#### Scenario: Slot único sin fecha_unica
- **WHEN** un PROFESOR envía `POST /api/encuentros/slots` sin `fecha_unica` y sin `cant_semanas`
- **THEN** el sistema rechaza con 422 indicando que debe especificar modo recurrente o único

### Requirement: Consultar slot con sus instancias
El sistema SHALL permitir obtener un slot de encuentro junto con todas sus instancias asociadas.

#### Scenario: Consulta de slot con instancias
- **WHEN** un usuario autenticado envía `GET /api/encuentros/slots/{id}` de un slot existente con 3 instancias
- **THEN** el sistema devuelve el slot con la lista de sus 3 instancias (fecha, hora, estado, meet_url, video_url)

#### Scenario: Slot no encontrado
- **WHEN** un usuario envía `GET /api/encuentros/slots/{id}` con un UUID que no existe
- **THEN** el sistema responde con 404

### Requirement: Generar bloque HTML para aula virtual
El sistema SHALL generar un fragmento HTML con el calendario de encuentros de un slot, listo para publicar en el LMS (F6.4).

#### Scenario: Generación exitosa de HTML
- **WHEN** un PROFESOR envía `GET /api/encuentros/slots/{id}/aula-virtual` de un slot con 2 instancias (1 Programada con meet_url, 1 Realizada con video_url)
- **THEN** el sistema devuelve `text/html` con una tabla que muestra fecha, horario, estado, enlace a videoconferencia y enlace a grabación

#### Scenario: Slot sin instancias
- **WHEN** un PROFESOR envía `GET /api/encuentros/slots/{id}/aula-virtual` de un slot sin instancias
- **THEN** el sistema devuelve HTML con mensaje indicando que no hay encuentros programados

### Requirement: Control de acceso para slots
El sistema SHALL requerir el permiso `encuentros:gestionar` para crear o modificar slots.

#### Scenario: Usuario sin permiso intenta crear slot
- **WHEN** un ALUMNO envía `POST /api/encuentros/slots`
- **THEN** el sistema responde con 403 Forbidden

#### Scenario: PROFESOR crea slot para su propia asignación
- **WHEN** un PROFESOR con permiso `encuentros:gestionar` crea un slot con su propio `asignacion_id`
- **THEN** el sistema permite la operación y asocia el slot al tenant del usuario

#### Scenario: PROFESOR crea slot con asignación de otro docente
- **WHEN** un PROFESOR intenta crear un slot con un `asignacion_id` que pertenece a otro usuario
- **THEN** el sistema rechaza con 403 (solo puede crear slots para sus propias asignaciones, a menos que sea COORDINADOR)

### Requirement: Aislamiento multi-tenant en slots
El sistema SHALL aislar los slots por tenant. Un usuario de un tenant no puede ver slots de otro tenant.

#### Scenario: Usuario de tenant A consulta slot de tenant B
- **WHEN** un usuario del tenant A envía `GET /api/encuentros/slots/{id}` de un slot del tenant B
- **THEN** el sistema responde con 404 (no 403, para no revelar existencia)
