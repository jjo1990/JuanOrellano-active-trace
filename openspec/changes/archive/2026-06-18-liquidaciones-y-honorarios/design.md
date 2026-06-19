## Context

C-18 es el último módulo backend pendiente del fork ancho (FASE 4). El sistema ya gestiona usuarios (C-07), estructura académica (C-06), asignaciones docente↔materia↔cohorte (C-07) y auditoría (C-05). FINANZAS necesita cerrar el ciclo administrativo calculando y liquidando honorarios docentes.

**Estado actual del código**:
- `Asignacion` existe con `usuario_id`, `rol`, `materia_id`, `cohorte_id`, `estado_vigencia`
- `Materia` tiene campos `id`, `tenant_id`, `codigo`, `nombre`, `estado`
- `Usuario` tiene campos bancarios (`cbu`, `alias_cbu`, `banco`) y `legajo`
- Clean Architecture: Routers → Services → Repositories → Models
- AES-256 para PII, soft delete, multi-tenant row-level

**PA-22 y PA-23 resueltas** (2026-06-18):
- PA-23: Plus acumula N veces (una por comisión de la misma categoría). RN-33/RN-34 ya lo especificaban.
- PA-22: `grupo_plus` (texto nullable) en Materia. Cada tenant define sus grupos. Sin catálogo fijo.

## Goals / Non-Goals

**Goals:**
- CRUD de grilla salarial: `SalarioBase` (monto por rol con vigencia) y `SalarioPlus` (adicional por grupo × rol con vigencia)
- Cálculo de liquidación: `Total = Base(rol) + Σ(Plus(grupo, rol) × N_comisiones)` por (docente, cohorte, mes)
- Cierre inmutable de liquidación (Abierta → Cerrada)
- Segmentación contable: general / NEXO (separado, suma al total) / facturantes (excluidos del total)
- ABM de facturas de monotributistas con cambio de estado Pendiente ↔ Abonada
- Validación de datos bancarios (sin CBU → no se liquida)
- Auditoría completa de todas las operaciones

**Non-Goals:**
- Integración con sistemas bancarios externos
- Generación de archivos de pago
- Cálculo de retenciones impositivas
- Notificaciones automáticas a docentes
- Exportación a formato de factura electrónica AFIP
- Módulo de corrección asistida (Épica 12)

## Decisions

### D1: grupo_plus como campo en Materia (no tabla aparte)

**Alternativa considerada**: tabla `materia_plus_grupo` con vigencia temporal.

**Decisión**: campo `grupo_plus VARCHAR NULL` en `materias`.

**Razón**: la KB define el mapeo como "configuración del tenant", no como un historial versionado. Agregar una tabla de join con vigencia agrega complejidad innecesaria. Si en el futuro se requiere historial, se migra el campo a una tabla — es un cambio no destructivo.

### D2: Liquidación pre-calculada y persistida

**Alternativa considerada**: vista computada on-the-fly sin persistencia.

**Decisión**: la liquidación se calcula y se persiste en estado `Abierta`. Solo se recalcula si se solicita explícitamente (cambios en la grilla o asignaciones).

**Razón**: la liquidación es un documento contable con ciclo de vida (Abierta → Cerrada). Debe persistirse para auditoría, historial y trazabilidad. La inmutabilidad post-cierre requiere estado persistido.

### D3: Una liquidación por (usuario, cohorte, mes)

Si un docente tiene múltiples roles (ej: PROFESOR + TUTOR), se genera una sola liquidación. El `monto_base` se toma del rol de mayor jerarquía según las asignaciones vigentes. Los plus se acumulan de todas sus comisiones activas, independientemente del rol.

**Alternativa considerada**: liquidaciones separadas por rol.

**Razón**: RN-34 define UNA fórmula por docente. FL-08 describe "por cada docente […] el sistema computa Base + Σ Plus". Dividir por rol complicaría el cierre (¿se cierran juntas o separadas?) y la vista de FINANZAS.

### D4: Cálculo de base — rol con asignaciones vigentes

Para determinar el `monto_base` de un docente:
1. Se consultan sus `Asignacion` vigentes en la cohorte y período
2. Se extraen los roles distintos
3. Se busca `SalarioBase` vigente para cada rol
4. Se toma el de mayor monto (o el único si hay uno solo)

Si no hay `SalarioBase` vigente para ningún rol → el docente no se liquida (se omite con advertencia).

### D5: Plus por comisión, no por materia

El multiplicador N en `Plus × N_comisiones` cuenta **comisiones** (instancias de asignación), no materias. Si un docente tiene 2 comisiones de PROG_I (misma materia, distintas divisiones), acumula 2× el plus de PROG.

**Razón**: RN-33 dice "N comisiones de la misma categoría". La unidad de trabajo docente es la comisión, no la materia.

### D6: Segmentación en el servicio, no en el modelo

La separación general / NEXO / facturantes (F10.6) se implementa como lógica de presentación en `LiquidacionService`, no como tablas separadas. El campo `es_nexo` (booleano) y `excluido_por_factura` (booleano) en `Liquidacion` permiten filtrar y agrupar.

### D7: Endpoints REST separados por recurso

- `/api/salarios/base` — CRUD SalarioBase (solo FINANZAS)
- `/api/salarios/plus` — CRUD SalarioPlus (solo FINANZAS)
- `/api/liquidaciones` — calcular, listar, ver detalle, cerrar, historial (FINANZAS, ADMIN)
- `/api/facturas` — CRUD + cambiar estado (FINANZAS)

**Razón**: alineado con el patrón del proyecto (routers separados por dominio). Cada router declara sus guards de permiso.

### D8: Validación de datos bancarios al calcular

Al calcular la liquidación, si un docente no tiene `cbu` y `alias_cbu` registrados, se omite de la liquidación con un warning en la respuesta (RN-26). No se bloquea el cálculo completo — solo se saltea ese docente.

## Risks / Trade-offs

- **[Riesgo] Inconsistencia si la grilla salarial cambia mientras una liquidación está Abierta**: el cálculo usa los valores vigentes al momento de ejecutar `POST /api/liquidaciones/calcular`. Si la grilla se modifica después, la liquidación abierta no se actualiza automáticamente. → **Mitigación**: endpoint explícito para recalcular una liquidación abierta. El cierre congela todo.
- **[Riesgo] Performance en tenant con cientos de docentes y miles de asignaciones**: el cálculo recorre todas las asignaciones vigentes. → **Mitigación**: queries optimizadas con joins en repository. Si escala, se puede agregar caché de asignaciones por cohorte.
- **[Trade-off] grupo_plus en Materia limita flexibilidad futura**: si se necesita historial de cambios de grupo, habrá que migrar. → **Aceptado**: YAGNI. La KB no pide historial de grupos.
- **[Riesgo] Edge case: docente sin asignaciones vigentes pero con liquidación histórica**: no afecta — las liquidaciones cerradas son históricas y no se recalculan.
