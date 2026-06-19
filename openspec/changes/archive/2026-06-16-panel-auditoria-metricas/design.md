## Context

C-05 implementó `AuditLog` (modelo, repositorio append-only, migración 006, trigger DB) y el endpoint `GET /audit-log`. C-19 agrega endpoints de agregación y panel sobre esos datos. Sin modelos nuevos.

**Restricciones**: solo lectura. Reusa `AuditLogRepository`. Nuevo permiso `auditoria:ver`.

## Goals / Non-Goals

**Goals:**
- `GET /api/auditoria/panel` — 4 secciones agregadas (F9.1). Guard: `auditoria:ver`.
- `GET /api/auditoria/log` — log completo con filtros (F9.2). Guard: `auditoria:ver`.
- Scope `(propio)` para COORDINADOR: solo ve datos de materias donde tiene asignación.
- Límite configurable de últimas acciones (default 200).
- Nuevo permiso `auditoria:ver` (ADMIN, COORDINADOR).

**Non-Goals:**
- Sin UI (→ C-24).
- Sin exportación (futuro).
- Sin gráficos (el frontend arma las visualizaciones).

## Decisions

### D1 — Un solo endpoint de panel con 4 secciones

`GET /api/auditoria/panel` devuelve un objeto con 4 keys: `acciones_por_dia`, `estado_comunicaciones`, `interacciones_docente_materia`, `ultimas_acciones`. El frontend consume una sola llamada.

### D2 — Scope (propio) para COORDINADOR

Si el usuario es COORDINADOR (no ADMIN), las queries de panel y log se filtran por las `materia_id` de sus asignaciones vigentes. ADMIN ve todo el tenant.

### D3 — Agregaciones con SQLAlchemy func y GROUP BY

Las queries de agregación usan `func.count()`, `func.date_trunc()` y `GROUP BY` sobre `AuditLog`. No se usa SQL raw — todo con SQLAlchemy ORM.

### D4 — Límite configurable vía query param

`GET /api/auditoria/panel?limite=100` o `GET /api/auditoria/log?limite=500`. Default 200.

### D5 — Layout

```
backend/app/
├── api/v1/routers/auditoria.py      # 🆕 (o extender audit_log.py)
├── services/auditoria_service.py    # 🆕
├── schemas/auditoria.py             # 🆕
├── core/action_codes.py             # ✅ + AUDITORIA_VER
└── alembic/versions/018_auditoria_ver.py  # 🆕 seed
```

## Migration Plan

1. Migración de datos: insertar `auditoria:ver` + RolPermiso (ADMIN, COORDINADOR). Idempotente.
