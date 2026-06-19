## ADDED Requirements

### Requirement: Crear convocatoria de coloquio
El sistema SHALL permitir a COORDINADOR y ADMIN crear una convocatoria de evaluación (F7.3) con materia, cohorte, tipo, instancia, días disponibles y cupos por día.

#### Scenario: Creación exitosa de convocatoria
- **WHEN** un COORDINADOR envía `POST /api/coloquios/evaluaciones` con `materia_id`, `cohorte_id`, `tipo=Coloquio`, `instancia=Coloquio Final`, `dias_disponibles=3` y `cupos_por_dia=5`
- **THEN** el sistema crea la evaluación y devuelve el recurso con estado Activa

#### Scenario: Creación con datos inválidos
- **WHEN** un COORDINADOR envía `POST /api/coloquios/evaluaciones` sin `materia_id`
- **THEN** el sistema rechaza con 422

#### Scenario: Usuario sin permiso intenta crear
- **WHEN** un ALUMNO envía `POST /api/coloquios/evaluaciones`
- **THEN** el sistema responde con 403

### Requirement: Listar convocatorias con métricas
El sistema SHALL listar todas las convocatorias del tenant con métricas operativas: materia, instancia, días disponibles, convocados, reservas activas, cupos libres (F7.4).

#### Scenario: COORDINADOR lista convocatorias
- **WHEN** un COORDINADOR envía `GET /api/coloquios/evaluaciones`
- **THEN** el sistema devuelve lista de evaluaciones con contadores: total_alumnos, reservas_activas, cupos_libres por día

#### Scenario: Filtrar convocatorias por cohorte
- **WHEN** un COORDINADOR envía `GET /api/coloquios/evaluaciones?cohorte_id={id}`
- **THEN** el sistema devuelve solo las evaluaciones de esa cohorte

### Requirement: Ver detalle de convocatoria
El sistema SHALL permitir ver el detalle de una convocatoria incluyendo alumnos cargados y reservas.

#### Scenario: Detalle de convocatoria con alumnos
- **WHEN** un COORDINADOR envía `GET /api/coloquios/evaluaciones/{id}` de una evaluación con 10 alumnos cargados y 3 reservas
- **THEN** el sistema devuelve la evaluación con listas de alumnos y reservas

### Requirement: Importar alumnos a convocatoria
El sistema SHALL permitir cargar el padrón de alumnos habilitados para una convocatoria (F7.2) mediante una lista de IDs de usuario.

#### Scenario: Importación exitosa de alumnos
- **WHEN** un COORDINADOR envía `POST /api/coloquios/evaluaciones/{id}/alumnos` con `alumnos=[{user_id: uuid1}, {user_id: uuid2}]`
- **THEN** el sistema crea registros de `ResultadoEvaluacion` con nota NULL para cada alumno nuevo, y omite los que ya existen

#### Scenario: Importación de alumno duplicado
- **WHEN** un COORDINADOR importa un alumno que ya está en la convocatoria
- **THEN** el sistema omite ese alumno sin error (idempotente)

### Requirement: Editar convocatoria
El sistema SHALL permitir modificar los datos de una convocatoria existente (F7.5).

#### Scenario: Cerrar convocatoria
- **WHEN** un COORDINADOR envía `PUT /api/coloquios/evaluaciones/{id}` con `estado=Cerrada`
- **THEN** el sistema actualiza el estado y no se permiten nuevas reservas en esa convocatoria

#### Scenario: Modificar cupos
- **WHEN** un COORDINADOR actualiza `cupos_por_dia` de una convocatoria
- **THEN** el sistema acepta el nuevo valor para futuras reservas

### Requirement: Aislamiento multi-tenant
El sistema SHALL aislar las evaluaciones por tenant.

#### Scenario: Usuario de tenant A no ve evaluaciones de tenant B
- **WHEN** un usuario del tenant A consulta evaluaciones
- **THEN** el sistema solo devuelve evaluaciones del tenant A
