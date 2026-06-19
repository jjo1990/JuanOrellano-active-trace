## ADDED Requirements

### Requirement: Registrar resultado de evaluación
El sistema SHALL permitir registrar la nota final de un alumno en una evaluación (F7.5 resultados).

#### Scenario: Registro exitoso de nota
- **WHEN** un COORDINADOR envía `POST /api/coloquios/resultados` con `evaluacion_id`, `alumno_id` y `nota_final=8`
- **THEN** el sistema actualiza el `ResultadoEvaluacion` del alumno con la nota

#### Scenario: Registrar nota de alumno no importado
- **WHEN** un COORDINADOR intenta registrar nota de un alumno que no fue importado a la convocatoria
- **THEN** el sistema rechaza con 404 y mensaje "El alumno no está en la convocatoria"

#### Scenario: Sobrescribir nota existente
- **WHEN** un COORDINADOR registra una nota para un alumno que ya tiene nota
- **THEN** el sistema actualiza la nota (sobrescribe) y registra la fecha de modificación

### Requirement: Registro académico consolidado
El sistema SHALL permitir consultar todas las notas finales de coloquios con filtros (F7.5).

#### Scenario: COORDINADOR consulta registro consolidado
- **WHEN** un COORDINADOR envía `GET /api/coloquios/resultados`
- **THEN** el sistema devuelve todos los resultados con nota del tenant, incluyendo datos de alumno, materia y cohorte

#### Scenario: Filtrar resultados por materia
- **WHEN** un COORDINADOR envía `GET /api/coloquios/resultados?materia_id={id}`
- **THEN** el sistema devuelve solo los resultados de esa materia

#### Scenario: Filtrar resultados sin nota
- **WHEN** un COORDINADOR envía `GET /api/coloquios/resultados?pendientes=true`
- **THEN** el sistema devuelve solo los resultados con nota NULL (pendientes de evaluación)

### Requirement: Control de acceso en resultados
El sistema SHALL requerir el permiso `coloquios:gestionar` para registrar y consultar resultados.

#### Scenario: ALUMNO consulta sus propios resultados
- **WHEN** un ALUMNO envía `GET /api/coloquios/resultados`
- **THEN** el sistema devuelve solo los resultados de ese ALUMNO (self-data)

#### Scenario: Usuario sin permiso intenta registrar nota
- **WHEN** un PROFESOR envía `POST /api/coloquios/resultados`
- **THEN** el sistema responde con 403
