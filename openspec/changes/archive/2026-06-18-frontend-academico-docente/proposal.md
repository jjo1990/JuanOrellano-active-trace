## Why

Los PROFESORES y TUTORES necesitan una interfaz visual para el ciclo completo de gestión de comisión: importar calificaciones del LMS, analizar el rendimiento de alumnos, detectar atrasados y comunicarse con ellos. El backend ya expone todos los endpoints necesarios (C-10 calificaciones, C-11 análisis, C-12 comunicaciones). Sin el frontend, los docentes no pueden usar estas capacidades. Es el primer feature module productivo después del shell de auth (C-21).

## What Changes

- **Nuevo feature module** `features/academico/` con estructura feature-based (components, hooks, pages, services, types)
- **Página de importación**: upload de archivo de calificaciones, vista previa de actividades/alumnos detectados, selección de actividades a incluir, confirmación de importación (F1.1)
- **Página de configuración de umbral**: slider/input de porcentaje por materia, valor por defecto 60% (F2.1)
- **Dashboard de materia**: tabla de atrasados, ranking de actividades aprobadas, notas finales agrupadas, reportes rápidos (F2.2-F2.5)
- **Página de comunicación**: preview de mensaje a atrasados, selección de destinatarios, envío con tracking de estado en tiempo real (F3.1-F3.3)
- **Monitor de seguimiento**: vista filtrable del estado de actividades de alumnos asignados (F2.8)
- **Servicios HTTP**: hooks de TanStack Query consumiendo `/api/calificaciones/*`, `/api/analisis/*`, `/api/comunicaciones/*`
- **Componentes compartidos**: tabla de datos con ordenamiento/filtros, indicador de estado, preview de mensaje
- **Rutas**: integración en el router con guards de permiso (`calificaciones:importar`, `atrasados:ver`, `comunicacion:enviar`)

## Capabilities

### New Capabilities
- `import-calificaciones`: UI para subir archivo de calificaciones, vista previa con detección de columnas, selección de actividades e importación.
- `umbral-configuracion`: UI para configurar el umbral de aprobación por materia (porcentaje, defecto 60%).
- `dashboard-atrasados`: Vista de alumnos atrasados, ranking de aprobadas, notas finales agrupadas, reportes rápidos y exportación de TPs sin corregir.
- `comunicacion-atrasados`: Preview de mensaje, selección de destinatarios atrasados, envío y tracking de estado en tiempo real.
- `monitor-seguimiento`: Vista filtrable del estado de actividades de alumnos asignados al docente (tutor/profesor).

### Modified Capabilities
<!-- None - this is a new frontend feature consuming existing backend APIs -->

## Impact

- **Nuevo directorio**: `frontend/src/features/academico/` (components, hooks, pages, services, types)
- **Rutas nuevas**: `/materias/:id/importar`, `/materias/:id/umbral`, `/materias/:id/dashboard`, `/materias/:id/comunicar`, `/monitor`
- **Servicios HTTP**: hooks TanStack Query para `calificaciones`, `analisis`, `comunicaciones`
- **Dependencias backend**: C-10 (calificaciones-y-umbral), C-11 (analisis-atrasados-reportes), C-12 (comunicaciones-cola-worker)
- **Dependencias frontend**: C-21 (frontend-shell-y-auth) — reusa layout, guards, cliente HTTP
- **Componentes compartidos nuevos**: DataTable, StatusBadge, MessagePreview
