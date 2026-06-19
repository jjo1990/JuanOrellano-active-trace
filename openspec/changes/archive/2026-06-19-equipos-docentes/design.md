## Context

C-07 implementó el modelo `Asignacion`, su CRUD individual (`/api/asignaciones`), el repositorio `AsignacionRepository` y el servicio `AsignacionService`. El servicio `PermissionService` ya resuelve permisos efectivos desde `Asignacion` vigentes. El permiso `equipos:asignar` existe y está otorgado a COORDINADOR y ADMIN.

C-08 construye la capa de operaciones a nivel equipo sobre esa base. El coordinador no opera asignación por asignación: necesita vistas consolidadas, operaciones en bloque, clonación entre períodos y exportación. El flujo FL-03 (setup de cuatrimestre) describe el caso de uso real: clonar equipo del período anterior → completar faltantes con asignación masiva → ajustar vigencias.

**Restricciones**:
- No se modifica el modelo `Asignacion` (sin nuevas columnas, sin migración de schema).
- Todos los endpoints nuevos van bajo el prefijo `/api/equipos` en un router separado.
- El repositorio `AsignacionRepository` se extiende con métodos nuevos.
- Se crea un nuevo servicio `EquipoService` para operaciones de equipo (no se mezclan con el CRUD individual de `AsignacionService`).
- Se agrega el permiso `equipos:ver_propio` para F4.2, separándolo de `equipos:asignar`.

## Goals / Non-Goals

**Goals:**
- Implementar `GET /api/equipos/mis-equipos` con joins a `user`, `rol`, `materia`, `carrera`, `cohorte` y filtros por estado, materia, rol, carrera, cohorte. Acceso: cualquier usuario autenticado (self-data).
- Implementar `POST /api/equipos/asignacion-masiva` con procesamiento best-effort (crea las válidas, reporta errores individuales sin detener el lote). Guard: `equipos:asignar`.
- Implementar `POST /api/equipos/clonar` que duplica asignaciones no eliminadas entre cohortes (RN-12). Guard: `equipos:asignar`.
- Implementar `PUT /api/equipos/vigencia` que actualiza `desde`/`hasta` masivamente con filtro de equipo. Guard: `equipos:asignar`.
- Implementar `GET /api/equipos/exportar` que genera CSV descargable con detalle del equipo. Guard: `equipos:asignar`.
- Implementar `GET /api/equipos/buscar-usuarios?q=` para autocompletado (RN-30).
- Agregar permiso `equipos:ver_propio` a PROFESOR, TUTOR, NEXO, COORDINADOR vía migración de datos.
- Extender `AsignacionRepository` con `list_with_joins`, `bulk_create`, `bulk_update_vigencia`, `list_by_equipo`.

**Non-Goals:**
- No se modifica el modelo `Asignacion` ni su tabla. Sin migración de schema (solo migración de datos para el nuevo permiso).
- No se implementa UI frontend (→ C-23).
- No se implementa F4.3 (consulta y gestión de asignaciones individuales) — ya está cubierto por los endpoints CRUD de C-07.
- No se implementa F4.1 (administración de usuarios del equipo docente) — es gestión de usuarios con datos PII, cubierto en C-07.
- No se exporta en formatos distintos a CSV (Excel, PDF → futuro).

## Decisions

### D1 — Router separado: `/api/equipos` vs extender `/api/asignaciones`

Se crea un nuevo router `equipos.py` bajo `api/v1/routers/` con prefijo `/api/equipos`. Esto separa conceptualmente:
- `/api/asignaciones`: CRUD individual de asignaciones (C-07).
- `/api/equipos`: operaciones a nivel equipo (vistas enriquecidas, bulk, clonación, exportación).

**Alternativa descartada**: agregar endpoints al router `asignaciones.py`. Se descarta porque:
- El router de asignaciones ya tiene 74 líneas con 5 endpoints; agregar 6 más lo llevaría a ~200 LOC.
- La separación semántica (`asignaciones` = CRUD individual, `equipos` = operaciones de equipo) es más clara para el frontend.
- Facilita tests separados por responsabilidad.

### D2 — Servicio separado: `EquipoService` vs extender `AsignacionService`

Se crea `services/equipo_service.py` con `EquipoService` que recibe `AsyncSession` y `tenant_id`. Este servicio:
- Usa directamente `AsignacionRepository` para queries (sin pasar por `AsignacionService`).
- Usa `UserRepository` para búsqueda de usuarios.
- Contiene la lógica de negocio de equipo: clonación, bulk create con errores individuales, bulk update, generación CSV.

**Alternativa descartada**: extender `AsignacionService`. Se descarta porque:
- `AsignacionService` ya tiene 188 líneas; agregar operaciones de equipo lo llevaría muy cerca de 500 LOC.
- Son responsabilidades distintas: CRUD individual vs operaciones masivas de equipo.
- Permite testear el servicio de equipo de forma aislada.

### D3 — F4.2 "Mis equipos": permiso `equipos:ver_propio` vs sin permiso vs `equipos:asignar`

Se crea el permiso `equipos:ver_propio`, otorgado a PROFESOR, TUTOR, NEXO, COORDINADOR. F4.2 usa `require_permission("equipos:ver_propio")`.

**Alternativas descartadas**:
- **Sin control de permiso** (solo `get_current_user`): cualquier usuario autenticado (incluyendo ALUMNO) vería "mis equipos", lo cual no es correcto semánticamente.
- **Usar `equipos:asignar`**: PROFESOR y TUTOR no tienen `equipos:asignar` (solo COORDINADOR y ADMIN), pero F4.2 dice explícitamente que PROFESOR, TUTOR y NEXO deben ver sus equipos. Darles `equipos:asignar` les permitiría modificar asignaciones, lo cual es un escalation de privilegios.
- **`context_check` con lambda**: demasiado frágil para un endpoint de lista.

La creación de un permiso separado sigue el principio de least privilege y es coherente con el modelo RBAC fino del sistema.

### D4 — Asignación masiva: estrategia best-effort

Cada usuario en el lote se procesa individualmente: si uno falla (FK inválida, usuario inexistente), se registra el error y se continúa con el siguiente. No hay rollback de la transacción completa.

**Alternativa descartada**: transacción todo-o-nada. Se descarta porque:
- La operación está diseñada para el COORDINADOR que selecciona 10-20 docentes de una lista; si uno tiene un problema, no quiere rehacer todo el trabajo.
- El frontend puede mostrar los errores puntuales y permitir corrección individual.
- Coherente con RN-30: la búsqueda con autocompletado minimiza la probabilidad de errores de FK.

**Implementación**: el endpoint recibe `{usuarios: [{id: uuid}], ...contexto_comun}`. Itera sobre usuarios, valida FK para cada uno, crea asignación. Errores se acumulan en una lista `errores`. La respuesta incluye `asignaciones_creadas`, `errores`, `total_procesados`, `total_exitosos`, `total_fallidos`.

### D5 — Clonación de equipo: qué se copia y qué no

Al clonar de origen a destino:
- **Se copia**: `usuario_id`, `rol_id`, `materia_id`, `carrera_id`, `comisiones`, `responsable_id`.
- **Se reemplaza**: `cohorte_id` → cohorte destino, `desde` y `hasta` → fechas del request.
- **No se copia**: `id` (nuevo UUID), `tenant_id` (heredado del contexto), `created_at`/`updated_at` (auto-generados), `deleted_at` (siempre NULL en el nuevo).
- **Se excluyen**: asignaciones con `deleted_at IS NOT NULL` del origen.

**Decisión de diseño**: las fechas de vigencia NO se heredan del origen porque el nuevo período tiene sus propias fechas. El request DEBE incluir `desde` y `hasta` para el destino (RN-12 habla de "duplica con las fechas correspondientes al destino").

### D6 — Exportación: CSV con `csv.writer` de stdlib

Se usa `csv.writer` del módulo estándar de Python para generar el CSV. La respuesta es `StreamingResponse` con `Content-Type: text/csv`. No se usa pandas ni openpyxl (evitar dependencias innecesarias).

**Columnas del CSV**: `Nombre`, `Apellido`, `Email`, `Legajo`, `Rol`, `Materia`, `Carrera`, `Cohorte`, `Comisiones`, `Desde`, `Hasta`, `Estado`.

**Alternativa descartada**: Excel (.xlsx). Se descarta por:
- Añade dependencia `openpyxl`.
- CSV es suficiente para la necesidad del coordinador (abrir en planilla de cálculo, procesar, compartir).
- Si en el futuro se requiere Excel, se puede agregar como formato alternativo.

### D7 — Filtros en modificar vigencia: al menos uno requerido

`PUT /api/equipos/vigencia` requiere al menos uno de `materia_id`, `carrera_id`, `cohorte_id` en el body. Esto evita la actualización masiva accidental de TODAS las asignaciones del tenant (defense in depth).

### D8 — Layout de archivos

```
backend/app/
├── api/v1/routers/
│   └── equipos.py                  # 🆕 Router con 6 endpoints
├── services/
│   └── equipo_service.py           # 🆕 EquipoService (≤200 LOC)
├── schemas/
│   └── equipo.py                   # 🆕 Schemas: MisEquiposResponse, AsignacionMasivaRequest/Response, etc.
├── repositories/
│   ├── asignacion_repository.py    # ✅ MODIFICADO: +list_with_joins, bulk_create, bulk_update_vigencia, list_by_equipo
│   └── user_repository.py          # ✅ MODIFICADO: +search_by_name (autocompletado)
├── core/
│   └── action_codes.py             # ✅ MODIFICADO: +EQUIPO_VER_PROPIO
└── tests/
    ├── test_equipos_mis_equipos.py     # 🆕
    ├── test_equipos_asignacion_masiva.py  # 🆕
    ├── test_equipos_clonar.py           # 🆕
    ├── test_equipos_vigencia.py         # 🆕
    ├── test_equipos_exportar.py         # 🆕
    └── test_equipos_busqueda.py         # 🆕
```

### D9 — Permiso `equipos:ver_propio` y migración

Se agrega el action code `EQUIPO_VER_PROPIO = "equipos:ver_propio"` en `core/action_codes.py`. Se crea una migración de datos que:
1. Inserta el permiso `equipos:ver_propio` en la tabla `permiso`.
2. Inserta registros `RolPermiso` para PROFESOR, TUTOR, NEXO, COORDINADOR.

Es una migración de datos (no de schema) porque las tablas `permiso` y `rol_permiso` ya existen desde C-04.

### D10 — `list_with_joins`: enfoque con SQLAlchemy joinedload

Para obtener datos enriquecidos en una sola query sin N+1, se usa `selectinload` o `joinedload` de SQLAlchemy sobre las relaciones FK del modelo `Asignacion`. El modelo ya tiene las FK definidas; se agregan `relationship()` al modelo `Asignacion` para que SQLAlchemy pueda eager-loadear las entidades relacionadas.

**Precaución**: `relationship()` se agrega como atributo de ORM, no como columna. No requiere migración de schema.

## Risks / Trade-offs

- **[Asignación masiva best-effort: inconsistencias si el coordinador reinterpreta errores]**: si 8 de 10 se crean y 2 fallan, el coordinador podría no notar los fallos → Mitigación: la respuesta incluye `total_exitosos`, `total_fallidos` y la lista de `errores` con detalle por usuario. El frontend debe mostrar un resumen claro (C-23).
- **[Clonación: no detecta duplicados lógicos]**: si se clona dos veces el mismo equipo al mismo destino, se crean asignaciones duplicadas (mismo usuario × rol × materia × cohorte) → Mitigación: es responsabilidad del coordinador no clonar dos veces. No se agrega constraint UNIQUE porque un docente PUEDE tener múltiples asignaciones legítimas al mismo contexto con diferentes `comisiones` o `responsable_id`.
- **[`selectinload` en `list_with_joins` puede generar queries grandes]**: cargar 5 relaciones por cada asignación → Mitigación: el volumen de asignaciones por equipo es típicamente < 50 docentes. Si escala, se puede paginar.
- **[CSV con `csv.writer`: no escapa fórmulas de Excel]**: si un nombre contiene `=` o `@`, Excel podría interpretarlo como fórmula → Mitigación: se prefijan las celdas que empiezan con `=`, `+`, `-`, `@` con una comilla simple (`'`). Implementación estándar de seguridad CSV.
- **[Nuevo `relationship()` en modelo `Asignacion` puede afectar queries existentes]**: agregar `relationship()` no debería cambiar el comportamiento de queries existentes que usan `select()` explícito. Los tests de C-07 verifican que nada se rompa.

## Migration Plan

1. **Migración de datos (Alembic)**: nueva migración que inserta el permiso `equipos:ver_propio` y sus `RolPermiso` asociados. Es idempotente (verifica si ya existe antes de insertar).
2. **Deploy**: sin migración de schema. El nuevo código es aditivo (nuevos endpoints, nuevo servicio). No hay breaking changes en la API de C-07.
3. **Rollback**: eliminar el router `equipos.py` del registro en `api/v1/__init__.py` y revertir la migración de datos. Las asignaciones existentes no se ven afectadas.

## Open Questions

- **¿Debe `mis-equipos` incluir asignaciones vencidas por defecto o solo vigentes?** La KB indica filtro de estado como opcional. El diseño propone devolver todas (vigentes + vencidas) por defecto, con filtro `?vigente=true` para acotar. Esto permite al docente ver su historial.
- **¿La búsqueda de usuarios (`buscar-usuarios`) debe filtrar por roles?** El spec incluye filtro opcional `roles=PROFESOR,TUTOR`. El diseño lo implementa como parámetro opcional. Sin el filtro, busca entre todos los usuarios del tenant.
- **¿Exportar equipo debería aceptar `formato=xlsx`?** Por ahora solo CSV. Si el frontend necesita Excel, se puede agregar en una iteración futura.
- **¿La clonación debe notificar a los docentes clonados?** No. La clonación es una operación administrativa silenciosa. La notificación es parte del flujo de avisos (C-15).
