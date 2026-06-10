## Context

El backend ya tiene auth JWT (C-03), RBAC con permisos finos (C-04) y audit log (C-05). La KB define Carrera (E1), Cohorte (E2) y Materia (E3) como las entidades raíz de la estructura académica. ADR-006 (docs/ARQUITECTURA.md §10) establece el patrón Materia + Dictado, pero C-06 cubre solo el catálogo — Dictado queda para C-07 o posterior.

**Estado actual:**
- `BaseModelMixin` disponible con `id`, `tenant_id`, `created_at`, `updated_at`, `deleted_at`
- `require_permission("estructura:gestionar")` ya existe en la matriz seed de C-04 (permiso asociado a ADMIN)
- No existen modelos de estructura académica aún
- Última migración: 006 (audit log)
- Convención: repositorios con tenant scope, schemas Pydantic con `extra='forbid'`

**Restricciones:**
- Multi-tenancy row-level: toda tabla lleva `tenant_id`
- Soft-delete siempre
- ≤500 LOC por archivo
- snake_case en todo Python

## Goals / Non-Goals

**Goals:**
- Modelos `Carrera`, `Cohorte`, `Materia` con herencia de `BaseModelMixin`
- Migración 007 con las tres tablas e índices de unicidad
- Schemas Pydantic request/response con `extra='forbid'`
- Services con la regla "carrera inactiva no admite cohortes activas"
- Repositories con tenant scope automático
- Endpoints CRUD protegidos con `require_permission("estructura:gestionar")`
- Tests: CRUD, unicidad por tenant, aislamiento multi-tenant, estado activa/inactiva

**Non-Goals:**
- No se implementa el modelo `Dictado` (ADR-006) — queda para C-07 o posterior
- No se implementa UI frontend
- No se implementan búsquedas avanzadas ni paginación (solo listado simple)
- No se implementan filtros por estado ni ordenamiento

## Decisions

### D1: Un archivo de repositorio único vs separado por entidad
- **Opción A (elegida)**: Un solo `EstructuraRepository` con métodos por entidad
- **Opción B**: `CarreraRepository`, `CohorteRepository`, `MateriaRepository` separados
- **Por qué A**: Las tres entidades comparten el mismo patrón CRUD y viven en el mismo módulo. Un solo repositorio evita duplicación de código boilerplate y mantiene ≤500 LOC. Si crece, se separa después.

### D2: Service único con sub-métodos
- **Opción A (elegida)**: Un `EstructuraService` que agrupa toda la lógica de las tres entidades
- **Opción B**: Services separados por entidad
- **Por qué A**: La regla de negocio "carrera inactiva" cruza Carrera ↔ Cohorte. Tenerlos en el mismo service facilita esa validación transversal. Un solo archivo.

### D3: Router único vs separado
- **Opción A (elegida)**: Un router `estructura.py` con los tres grupos de endpoints bajo prefijos `/admin/carreras`, `/admin/cohortes`, `/admin/materias`
- **Opción B**: Tres routers separados
- **Por qué A**: Un solo archivo es más cohesivo para el módulo. FastAPI soporta múltiples prefijos en un mismo router vía `APIRouter(prefix="/api/admin")`.

### D4: Manejo de unicidad con UniqueConstraint + DB
- **Opción A (elegida)**: `UniqueConstraint` en los modelos + catch de excepción de integridad en service
- **Opción B**: Validación en service con SELECT antes de INSERT
- **Por qué A**: La DB es la fuente de verdad de unicidad. Validar en service introduce race conditions (TOCTOU). El catch de `IntegrityError` en el service es más robusto.

### D5: `vig_hasta` nullable = cohorte abierta
- **Opción A (elegida)**: `vig_hasta` nullable; `null` significa "abierta sin fecha de cierre"
- **Opción B**: Campo booleano `abierta` separado
- **Por qué A**: Consistente con todas las demás entidades del modelo (04_modelo_de_datos.md §Convenciones). Un campo nullable evita data duplicada y posibles inconsistencias.

### D6: Estado activa/inactiva como booleano
- **Opción A (elegida)**: `estado: bool` — `True` = activa, `False` = inactiva
- **Opción B**: Enum con `Activa/Inactiva`
- **Por qué A**: La KB usa "enum" conceptual pero el modelo solo tiene dos estados. Booleano es más simple y eficiente. Si en el futuro se agregan estados, se migra a un enum.

### D7: Checkpoint de validación post-implementación
- **Checkpoint 1**: Verificar que `(tenant_id, codigo)` tenga unique index en carrera y materia
- **Checkpoint 2**: Verificar que `(tenant_id, carrera_id, nombre)` tenga unique index en cohorte
- **Checkpoint 3**: Verificar que el service rechace cohorte activa ligada a carrera inactiva
- **Checkpoint 4**: Verificar que un usuario del tenant A no pueda modificar datos del tenant B

## Risks / Trade-offs

| Riesgo | Mitigación |
|--------|-----------|
| **R1**: Unicidad catch de IntegrityError puede tragar errores no esperados | Loggear el error original antes de lanzar HTTPException 409. Tests específicos para cada constraint |
| **R2**: Un solo archivo de repository puede exceder 500 LOC si crece | Monitorear LOC. Si se acerca al límite, separar por entidad |
| **R3**: `vig_hasta` nullable puede dar lugar a cohortes que quedan abiertas para siempre | Política de negocio: al cerrar una carrera, forzar cierre de todas sus cohortes. Esto se implementa en el service |
| **R4**: El permiso `estructura:gestionar` debe existir en seed | Verificar en el archivo de seed de C-04 que el permiso esté presente en el catálogo y asociado a ADMIN |

## Migration Plan

### Forward (007_estructura_academica.py)
1. Crear tabla `carrera` con `UniqueConstraint(tenant_id, codigo)` + índice
2. Crear tabla `cohorte` con `UniqueConstraint(tenant_id, carrera_id, nombre)` + FK a carrera + índice
3. Crear tabla `materia` con `UniqueConstraint(tenant_id, codigo)` + índice

### Rollback (downgrade)
1. Dropear tabla `materia`
2. Dropear tabla `cohorte`
3. Dropear tabla `carrera`

## Open Questions

- **OQ1**: `vig_hasta` nulo en cohorte = abierta. ¿Se necesita un endpoint específico para "cerrar" una cohorte? Decisión: el PUT de cohorte permite setear `vig_hasta`. No se necesita acción separada por ahora.
- **OQ2**: ¿Se permite crear cohortes sin fecha `vig_desde`? Decisión: no, es requerido — toda cohorte tiene una fecha de inicio conocida.
