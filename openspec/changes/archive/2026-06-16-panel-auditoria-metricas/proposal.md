## Why

C-05 construyó el modelo `AuditLog` con registro append-only de todas las acciones del sistema, pero no existen endpoints de consulta agregada: el COORDINADOR no puede ver quién está activo, cómo van las comunicaciones, ni qué docentes están inactivos. Sin el panel de métricas (F9.1) y el log completo (F9.2), la trazabilidad que promete el sistema es invisible. Este change expone los datos de auditoría como paneles de supervisión y monitoreo.

## What Changes

- **F9.1 — Panel de interacciones**: endpoint `GET /api/auditoria/panel` con 4 sub-vistas agregadas: (a) acciones por día, (b) estado de comunicaciones por docente, (c) interacciones por docente × materia, (d) log de últimas acciones (límite configurable, defecto 200). Filtros: rango de fechas, materia, usuario. Guard: `auditoria:ver`.
- **F9.2 — Log completo de auditoría**: endpoint `GET /api/auditoria/log` con filtros avanzados: fecha desde/hasta, materia, usuario, acción, IP. Solo ADMIN. Guard: `auditoria:ver`.
- **Nuevo permiso**: `auditoria:ver` (ADMIN, COORDINADOR). COORDINADOR con scope `(propio)`: solo ve datos de sus materias/asignaciones.
- **Nuevo servicio**: `AuditoriaService` con queries de agregación sobre `AuditLog`.
- **Migración de datos**: seed del permiso `auditoria:ver` + RolPermiso.

## Capabilities

### New Capabilities

- `panel-auditoria`: endpoint de agregación con métricas de uso, estado de comunicaciones, interacciones y log reciente.
- `log-auditoria`: consulta completa del registro de auditoría con filtros avanzados.

### Modified Capabilities

- `audit-log` (C-05): se agrega el permiso `auditoria:ver` al catálogo.

## Impact

- **Nuevo código**: `services/auditoria_service.py`, `api/v1/routers/auditoria.py` (o extensión de `audit_log.py`), `schemas/auditoria.py`.
- **Modificado**: `core/action_codes.py` (nuevo permiso), `main.py` (router).
- **Sin nuevos modelos**: reusa `AuditLog` de C-05.
- **Sin migración de schema**: solo migración de datos para el permiso.
- **Governance**: ALTO — expone datos de auditoría de todo el tenant. Requiere scope `(propio)` para COORDINADOR.
