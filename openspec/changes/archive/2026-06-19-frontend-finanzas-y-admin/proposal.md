## Why

Los roles FINANZAS y ADMIN necesitan interfaces visuales para sus operaciones críticas: liquidar honorarios docentes del período, gestionar la estructura académica del tenant, administrar usuarios, y auditar la actividad del sistema. El backend ya expone todos los endpoints (C-06 estructura, C-07 usuarios, C-18 liquidaciones, C-19 auditoría). C-24 es el último feature module productivo — cierra el frente frontend del producto.

## What Changes

- **Nuevo feature module** `features/finanzas/` con estructura feature-based (components, hooks, pages, services, types)
- **Nuevo feature module** `features/admin/` con estructura feature-based (components, hooks, pages, services, types)
- **Vista de liquidaciones del período**: tres segmentos (general / NEXO / factura), KPIs de cabecera (total sin factura / total con factura), filtros por cohorte, mes y docente (F10.1, F10.6)
- **Cerrar liquidación**: acción irreversible que inmuta la liquidación del período (F10.2)
- **Historial de liquidaciones**: consulta de períodos anteriores cerrados (F10.3)
- **Grilla salarial**: ABM de salarios base por rol y plus adicionales con vigencia temporal (F10.4)
- **Gestión de facturas**: ABM de comprobantes de docentes que facturan, con cambio de estado pendiente/abonada, filtros y búsqueda (F10.5)
- **Estructura académica**: ABM de carreras y cohortes (alta, edición, cambio de estado activa/inactiva) (F5.1, F5.2)
- **Usuarios del tenant**: alta, edición, activación/desactivación de usuarios con rol docente, datos bancarios, información de facturación (F4.1)
- **Panel de auditoría y métricas**: acciones por día, estado de comunicaciones, interacciones por docente y materia, log de últimas acciones con filtros (F9.1, F9.2)
- **Log completo de auditoría**: tabla con fecha, usuario, materia, acción, registros afectados, IP, user agent (F9.2)
- **Rutas**: integración en el router con guards de permiso de FINANZAS y ADMIN

## Capabilities

### New Capabilities
- `liquidaciones-periodo`: Vista de liquidaciones con segmentación general/NEXO/factura, KPIs de totales, filtros, cierre y detalle por docente.
- `historial-liquidaciones`: Consulta de liquidaciones de períodos anteriores cerrados.
- `grilla-salarial`: ABM de salarios base por rol y plus adicionales con vigencia temporal desde/hasta.
- `gestion-facturas`: ABM de comprobantes de docentes que facturan, cambio de estado pendiente/abonada, filtros y búsqueda.
- `estructura-academica-admin`: ABM de carreras y cohortes (alta, edición, cambio de estado activa/inactiva).
- `usuarios-tenant`: Alta, edición, activación/desactivación de usuarios del tenant con datos completos (rol, bancarios, facturación).
- `panel-auditoria`: Panel con métricas de uso: acciones por día, estado de comunicaciones, interacciones por docente/materia, log de últimas acciones con filtros.
- `log-auditoria-completo`: Tabla completa del log de auditoría con todos los campos registrados (fecha, usuario, materia, acción, IP, user agent).

### Modified Capabilities
<!-- None - this is a new frontend feature consuming existing backend APIs -->

## Impact

- **Nuevos directorios**: `frontend/src/features/finanzas/` y `frontend/src/features/admin/` (components, hooks, pages, services, types)
- **Rutas nuevas**: `/liquidaciones`, `/liquidaciones/historial`, `/salarios`, `/facturas`, `/estructura`, `/usuarios`, `/auditoria`, `/auditoria/log`
- **Servicios HTTP**: hooks TanStack Query para `liquidaciones`, `salarios`, `facturas`, `estructura`, `usuarios`, `auditoria`
- **Dependencias backend**: C-06 (estructura-academica), C-07 (usuarios), C-18 (liquidaciones), C-19 (auditoria)
- **Dependencias frontend**: C-21 (shell + auth), reusa DataTable, StatusBadge, RequirePermission de módulos anteriores
- **Menú**: nuevas secciones "Finanzas" y "Administración" en sidebar con dropdowns de módulos
