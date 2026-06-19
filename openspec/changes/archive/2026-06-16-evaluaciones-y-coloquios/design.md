## Context

C-06 (estructura-academica) y C-07 (usuarios-y-asignaciones) construyeron las entidades raíz: `Materia`, `Cohorte`, `User`, `Asignacion`. El sistema ya tiene RBAC fino con resolución de permisos. No existen reglas RN específicas para coloquios, pero el flujo FL-07 y la Épica 7 definen el comportamiento esperado.

C-14 modela el dominio de evaluaciones formales con reserva de turnos. El flujo FL-07 describe tres fases: preparación (COORDINADOR crea convocatoria e importa alumnos) → reserva (ALUMNO elige turno) → seguimiento (COORDINADOR ve agenda y registra resultados).

**Restricciones**:
- Nuevos modelos `Evaluacion`, `ReservaEvaluacion`, `ResultadoEvaluacion` con `BaseModelMixin`.
- Router único bajo prefijo `/api/coloquios`.
- Servicio único `ColoquioService` para toda la lógica.
- Todos los schemas Pydantic con `extra='forbid'`.
- Sin dependencias nuevas.
- PA-14 resuelto: el ALUMNO reserva desde dentro del sistema vía endpoint REST.

## Goals / Non-Goals

**Goals:**
- Modelos `Evaluacion`, `ReservaEvaluacion`, `ResultadoEvaluacion` con FK a `materia`, `cohorte`, `user`.
- `POST /api/coloquios/evaluaciones` — crear convocatoria con materia, cohorte, tipo, instancia, días disponibles, cupos por día (F7.3). Guard: `coloquios:gestionar`.
- `GET /api/coloquios/evaluaciones` — listado tabular con métricas por convocatoria (F7.4).
- `GET /api/coloquios/evaluaciones/{id}` — detalle de convocatoria con alumnos y reservas.
- `PUT /api/coloquios/evaluaciones/{id}` — editar/cerrar convocatoria (F7.5).
- `POST /api/coloquios/evaluaciones/{id}/alumnos` — importar alumnos habilitados (F7.2). Guard: `coloquios:gestionar`.
- `POST /api/coloquios/reservas` — ALUMNO reserva turno con validación de cupo. Guard: `coloquios:reservar`.
- `DELETE /api/coloquios/reservas/{id}` — ALUMNO cancela su reserva. Guard: `coloquios:reservar`.
- `GET /api/coloquios/agenda` — agenda consolidada de reservas activas con filtros (F7.5).
- `POST /api/coloquios/resultados` — registrar nota final (F7.5). Guard: `coloquios:gestionar`.
- `GET /api/coloquios/resultados` — registro académico consolidado (F7.5).
- `GET /api/coloquios/metricas` — panel de métricas agregadas (F7.1).
- Nuevos permisos: `coloquios:gestionar` (COORDINADOR, ADMIN) y `coloquios:reservar` (ALUMNO).

**Non-Goals:**
- No se modifica el modelo `Asignacion` ni `User`.
- No se implementa UI frontend (→ C-23).
- No se modela `FechaAcademica` (→ C-17).
- No se integra con Moodle para la reserva (es interna).
- No se implementan restricciones de regularidad para reservar (PA-14 — futuro).

## Decisions

### D1 — Router único: `/api/coloquios`

Todas las operaciones de coloquios van bajo un solo router `coloquios.py` con prefijo `/api/coloquios`. Aunque hay tres subdominios (evaluaciones, reservas, resultados), comparten el mismo permiso base y el mismo servicio.

**Alternativa descartada**: routers separados para cada subdominio. Se descarta porque:
- El servicio `ColoquioService` ya unifica la lógica; separar routers no agrega valor.
- Son ~10 endpoints en total, manejable en un solo archivo.

### D2 — Servicio único: `ColoquioService`

Un solo servicio `ColoquioService` que maneja evaluaciones, reservas y resultados. Recibe `AsyncSession` y `tenant_id`.

### D3 — Cupo: validación a nivel de servicio

Cada `Evaluacion` tiene un campo `cupos_por_dia` (entero). Al crear la convocatoria, el sistema no crea "slots" individuales — el cupo se valida dinámicamente: al reservar, se cuenta cuántas reservas Activas hay para esa fecha y se compara con el cupo.

**Alternativa descartada**: crear N "slots" de turno al crear la convocatoria. Se descarta porque:
- Agrega complejidad innecesaria (hay que crear, mantener y sincronizar slots).
- El cupo diario es un límite agregado simple.
- Si en el futuro se necesitan franjas horarias, se puede extender.

### D4 — Reserva: state machine simple

`ReservaEvaluacion` tiene estados `Activa` y `Cancelada`. Transiciones:
- Creación → Activa (si hay cupo)
- Activa → Cancelada (por ALUMNO o COORDINADOR)
- No se reabre una reserva cancelada (se crea una nueva)

**Soft delete**: cancelar una reserva NO es soft delete — es un cambio de estado a `Cancelada`. El soft delete se usa para eliminación administrativa.

### D5 — Import de alumnos: upsert por lista de IDs

`POST /api/coloquios/evaluaciones/{id}/alumnos` recibe una lista de `user_id`. El endpoint crea registros en `ResultadoEvaluacion` con `nota_final=NULL` (pendiente de evaluación) para cada alumno que no tenga ya un registro. Si el alumno ya existe en la convocatoria, se omite (no se duplica).

**Alternativa descartada**: importar archivo xlsx. Se descarta porque:
- La importación de padrones ya está cubierta en C-09.
- Acá alcanza con pasar los IDs de usuarios ya existentes en el sistema.

### D6 — Agenda consolidada: query con JOINs

`GET /api/coloquios/agenda` devuelve todas las reservas activas con datos de alumno, materia, cohorte y fecha. Filtros: `materia_id`, `cohorte_id`, `fecha_desde`, `fecha_hasta`, `q` (búsqueda por nombre de alumno).

### D7 — Layout de archivos

```
backend/app/
├── api/v1/routers/
│   └── coloquios.py                   # 🆕 Router: ~12 endpoints
├── services/
│   └── coloquio_service.py            # 🆕 ColoquioService (≤300 LOC)
├── schemas/
│   └── coloquio.py                    # 🆕 Schemas Pydantic
├── repositories/
│   ├── evaluacion_repository.py       # 🆕
│   ├── reserva_evaluacion_repository.py  # 🆕
│   └── resultado_evaluacion_repository.py  # 🆕
├── models/
│   ├── evaluacion.py                  # 🆕
│   ├── reserva_evaluacion.py          # 🆕
│   ├── resultado_evaluacion.py        # 🆕
│   └── __init__.py                    # ✅ MODIFICADO
├── core/
│   └── action_codes.py                # ✅ MODIFICADO
└── tests/
    ├── test_evaluacion_repository.py  # 🆕
    ├── test_coloquio_service.py       # 🆕
    └── test_coloquio_schemas.py       # 🆕
```

### D8 — Permisos: `coloquios:gestionar` y `coloquios:reservar`

- `coloquios:gestionar` → COORDINADOR, ADMIN (crear/editar convocatorias, importar alumnos, registrar resultados)
- `coloquios:reservar` → ALUMNO (reservar/cancelar turno)

El endpoint `GET /api/coloquios/evaluaciones` es público para usuarios autenticados (tanto COORDINADOR ve todas, como ALUMNO ve las que le corresponden).

## Risks / Trade-offs

- **[Cupo diario sin transacción atómica]**: dos alumnos podrían reservar simultáneamente el último cupo → Mitigación: usar `SELECT ... FOR UPDATE` en el count de reservas activas o un lock advisory. Para MVP, la probabilidad es baja (no es un sistema de venta de entradas).
- **[Import de alumnos sin validación de regularidad]**: cualquier alumno del tenant puede ser importado, sin verificar que esté inscripto en la materia → Mitigación: PA-14 queda abierto para agregar restricciones de regularidad en el futuro.
- **[No hay restricción de una reserva por alumno por evaluación]**: un alumno podría reservar múltiples turnos en la misma evaluación → Mitigación: agregar constraint UNIQUE `(evaluacion_id, alumno_id)` donde `estado = 'Activa'`. Se implementa como validación en el servicio.

## Migration Plan

1. **Migración de schema**: crear tablas `evaluacion`, `reserva_evaluacion`, `resultado_evaluacion` con FK e índices.
2. **Migración de datos**: insertar permisos `coloquios:gestionar` y `coloquios:reservar` + RolPermiso. Idempotente.
3. **Deploy**: código aditivo. Sin breaking changes.
4. **Rollback**: downgrade de migración + eliminar router de `main.py`.

## Open Questions

- **¿Debe el COORDINADOR poder cancelar una reserva de un ALUMNO?** → Sí, vía `DELETE /api/coloquios/reservas/{id}` con guard `coloquios:gestionar`.
- **¿El panel de métricas (F7.1) debe filtrarse por cohorte?** → Sí, se agrega `cohorte_id` como query param opcional.
- **¿Se debe notificar al ALUMNO cuando se registra su nota?** → No en este change. Es parte del flujo de comunicaciones (C-12).
