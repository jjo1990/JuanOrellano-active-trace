## Context

C-06 (estructura-academica) y C-07 (usuarios-y-asignaciones) construyeron las entidades raíz: `Materia`, `Carrera`, `Cohorte`, `Asignacion`. El sistema ya tiene usuarios con roles y asignaciones vigentes. Los permisos `encuentros:gestionar` y `guardias:registrar` no existen aún y deben crearse vía migración de datos.

C-13 modela el dominio de encuentros sincrónicos y guardias. El flujo FL-06 describe el caso de uso real: PROFESOR crea slot recurrente → el sistema genera instancias → PROFESOR edita instancia con grabación → COORDINADOR audita → se genera HTML para el LMS.

**Restricciones**:
- Nuevos modelos `SlotEncuentro`, `InstanciaEncuentro`, `Guardia` con `BaseModelMixin` (soft delete, timestamps, tenant_id).
- Routers separados: `/api/encuentros` y `/api/guardias`.
- Servicios separados: `EncuentroService` y `GuardiaService`.
- Todos los schemas Pydantic con `extra='forbid'`.
- Migración de schema (nuevas tablas) + migración de datos (nuevos permisos).
- Sin dependencias nuevas (no se agregan librerías).

## Goals / Non-Goals

**Goals:**
- Modelos `SlotEncuentro`, `InstanciaEncuentro`, `Guardia` con FK a `asignacion`, `materia`, `carrera`, `cohorte`.
- `POST /api/encuentros/slots` — crear slot recurrente (genera N instancias, RN-13) o único (genera 1 instancia). Guard: `encuentros:gestionar`.
- `POST /api/encuentros/instancias` — crear instancia independiente (sin slot padre). Guard: `encuentros:gestionar`.
- `PUT /api/encuentros/instancias/{id}` — editar estado, meet_url, video_url, comentario (RN-14). Guard: `encuentros:gestionar`.
- `GET /api/encuentros/slots/{id}` — ver slot con sus instancias asociadas.
- `GET /api/encuentros/slots/{id}/aula-virtual` — generar bloque HTML con calendario de encuentros y grabaciones (F6.4).
- `GET /api/encuentros/admin` — vista transversal de todos los encuentros del tenant con filtros (F6.5). Guard: `encuentros:gestionar`.
- `GET /api/encuentros/mis-encuentros` — encuentros del usuario autenticado según sus asignaciones.
- `POST /api/guardias` — registrar guardia cubierta (F6.6). Guard: `guardias:registrar`.
- `GET /api/guardias` — consulta filtrada por materia, carrera, cohorte, estado, fecha.
- `GET /api/guardias/exportar` — exportación CSV. Guard: `guardias:registrar`.
- Nuevos permisos: `encuentros:gestionar` (PROFESOR, COORDINADOR) y `guardias:registrar` (TUTOR, COORDINADOR, ADMIN).

**Non-Goals:**
- No se modifica el modelo `Asignacion` ni otros modelos existentes.
- No se implementa UI frontend (→ C-23).
- No se implementa integración con Google Meet/Zoom para crear salas automáticamente.
- No se implementa notificación a alumnos sobre nuevos encuentros (→ C-12 o C-15).
- No se exporta en formatos distintos a CSV para guardias.

## Decisions

### D1 — Dos routers separados: `/api/encuentros` y `/api/guardias`

Se crean dos routers bajo `api/v1/routers/`:
- `encuentros.py` con prefijo `/api/encuentros`: slots, instancias, vista admin, aula virtual.
- `guardias.py` con prefijo `/api/guardias`: CRUD de guardias, exportación CSV.

**Alternativa descartada**: un solo router `/api/encuentros-y-guardias`. Se descarta porque:
- Son dominios distintos: slots/instancias son planificación académica; guardias son registro operativo.
- Permisos distintos: `encuentros:gestionar` vs `guardias:registrar`.
- Facilita tests y mantenimiento separados.

### D2 — Servicios separados: `EncuentroService` y `GuardiaService`

- `EncuentroService`: lógica de generación de instancias (RN-13), generación HTML (F6.4), filtros de vista admin.
- `GuardiaService`: CRUD simple + generación CSV.

**Alternativa descartada**: un solo servicio. Se descarta por separación de responsabilidades y para mantenerse bajo 200 LOC por archivo.

### D3 — RN-13: Dos modos de creación de slot

El endpoint `POST /api/encuentros/slots` soporta dos modos excluyentes según el body:

1. **Recurrente**: `dia_semana` + `hora` + `fecha_inicio` + `cant_semanas` → genera N instancias, una por semana desde `fecha_inicio`.
2. **Único**: `fecha_unica` + `hora` → genera 1 instancia en esa fecha.

Validación: si `cant_semanas > 0` → modo recurrente (ignora `fecha_unica`). Si `cant_semanas == 0` o `null` → modo único (requiere `fecha_unica`).

El slot se persiste con ambos campos; las instancias se crean en la misma transacción.

**Cálculo de fechas para modo recurrente**: se toma `fecha_inicio`, se avanza al `dia_semana` correspondiente (si no coincide, se ajusta al próximo), y se generan `cant_semanas` instancias con 7 días de diferencia.

### D4 — RN-14: Estado de instancia independiente del slot

Cada `InstanciaEncuentro` tiene su propio campo `estado` (Programado, Realizado, Cancelado). Editar una instancia (`PUT /api/encuentros/instancias/{id}`) modifica solo esa instancia, sin afectar al slot padre ni a otras instancias del mismo slot.

El slot no tiene campo `estado` propio.

### D5 — Bloque HTML para aula virtual (F6.4)

`GET /api/encuentros/slots/{id}/aula-virtual` devuelve `text/html` con un fragmento HTML que lista:
- Título del slot
- Tabla con: fecha, horario, estado, enlace a videoconferencia, enlace a grabación (si disponible)

Se genera con un template string en Python (sin dependencia de Jinja2 para este caso simple). El HTML es un fragmento (no un documento completo) para que el docente lo embeba en el LMS.

### D6 — Exportación CSV de guardias con `csv.writer`

Se usa `csv.writer` del módulo estándar. Columnas: `Materia`, `Carrera`, `Cohorte`, `Tutor`, `Día`, `Horario`, `Estado`, `Comentarios`, `Fecha de registro`.

Respuesta: `StreamingResponse` con `Content-Type: text/csv` y header `Content-Disposition: attachment`.

### D7 — Guardia: `asignacion_id` como FK

El modelo `Guardia` referencia a `Asignacion` (`asignacion_id`) para identificar quién cubrió la guardia. También tiene FK redundantes a `materia_id`, `carrera_id`, `cohorte_id` para queries directas sin JOIN a `Asignacion`.

**Alternativa descartada**: solo `asignacion_id` y resolver materia/carrera/cohorte vía JOIN. Se descarta porque:
- Las queries de filtrado de guardias por materia/carrera/cohorte son el caso de uso principal.
- Las FK redundantes evitan JOINs costosos en queries de listado.

### D8 — Layout de archivos

```
backend/app/
├── api/v1/routers/
│   ├── encuentros.py              # 🆕 Router: slots, instancias, admin, aula-virtual
│   └── guardias.py                # 🆕 Router: CRUD guardias, export
├── services/
│   ├── encuentro_service.py       # 🆕 EncuentroService (generación instancias, HTML)
│   └── guardia_service.py         # 🆕 GuardiaService (CRUD + CSV)
├── schemas/
│   ├── encuentro.py               # 🆕 Schemas: SlotCreate/Response, InstanciaResponse, etc.
│   └── guardia.py                 # 🆕 Schemas: GuardiaCreate/Response, etc.
├── repositories/
│   ├── slot_encuentro_repository.py    # 🆕
│   ├── instancia_encuentro_repository.py  # 🆕
│   └── guardia_repository.py          # 🆕
├── models/
│   ├── slot_encuentro.py          # 🆕
│   ├── instancia_encuentro.py     # 🆕
│   ├── guardia.py                 # 🆕
│   └── __init__.py                # ✅ MODIFICADO: exports
├── core/
│   └── action_codes.py            # ✅ MODIFICADO: ENCUENTROS_GESTIONAR, GUARDIAS_REGISTRAR
└── tests/
    ├── test_slots.py              # 🆕
    ├── test_instancias.py         # 🆕
    ├── test_aula_virtual.py       # 🆕
    ├── test_guardias.py           # 🆕
    └── test_guardias_export.py    # 🆕
```

### D9 — Permisos: `encuentros:gestionar` y `guardias:registrar`

Se agregan constantes en `core/action_codes.py`:
- `ENCUENTROS_GESTIONAR = "encuentros:gestionar"`
- `GUARDIAS_REGISTRAR = "guardias:registrar"`

Migración de datos que:
1. Inserta ambos permisos en tabla `permiso`.
2. Inserta `RolPermiso`: `encuentros:gestionar` → PROFESOR, COORDINADOR; `guardias:registrar` → TUTOR, COORDINADOR, ADMIN.

### D10 — `GET /api/encuentros/mis-encuentros`: resolución por asignaciones

El endpoint consulta las asignaciones del usuario autenticado y devuelve los slots e instancias asociados a las materias de esas asignaciones. Sin permiso especial (self-data, como `mis-equipos` en C-08).

## Risks / Trade-offs

- **[Generación HTML sin sanitización]**: si el título del slot contiene HTML malicioso → Mitigación: escapar con `html.escape()` antes de interpolar en el template.
- **[Slot sin instancias si `cant_semanas = 0`]**: si se crea un slot recurrente con cant_semanas = 0, no genera instancias pero el slot queda huérfano → Mitigación: validar `cant_semanas >= 1` en modo recurrente.
- **[FK redundantes en Guardia pueden desincronizarse]**: si `asignacion_id` apunta a una materia X pero `materia_id` tiene Y → Mitigación: validar consistencia en el endpoint (las FK deben coincidir con la asignación). No se agrega constraint de BD para evitar complejidad.
- **[Instancias huérfanas al eliminar slot]**: si se hace soft-delete de un slot, las instancias quedan referenciando un slot eliminado → Mitigación: el repositorio de instancias debe filtrar `slot.deleted_at IS NULL` en queries que incluyan el slot.

## Migration Plan

1. **Migración de schema (Alembic)**: nueva migración que crea las tablas `slot_encuentro`, `instancia_encuentro`, `guardia` con sus FK, índices y constraints.
2. **Migración de datos (misma migración o siguiente)**: inserta los permisos `encuentros:gestionar` y `guardias:registrar` + sus `RolPermiso` asociados. Idempotente.
3. **Deploy**: código aditivo (nuevos endpoints, nuevos servicios). Sin breaking changes.
4. **Rollback**: downgrade de la migración (DROP TABLE) y eliminar registros de routers en `main.py`. Sin impacto en datos existentes.

## Open Questions

- **¿Debe `cant_semanas` tener un máximo?** El diseño no impone límite máximo; un slot de 52 semanas generaría 52 instancias, lo cual es razonable.
- **¿La generación de instancias debe manejar feriados?** No en este change. Si se requiere, se puede agregar un parámetro `excluir_fechas` en el futuro.
- **¿El bloque HTML debe incluir estilos CSS inline?** Sí, estilos mínimos para que se vea bien en el LMS sin depender de CSS externo.
