## 1. Setup — Módulo Finanzas

- [x] 1.1 Crear estructura `features/finanzas/` con subdirectorios: components, hooks, pages, services, types
- [x] 1.2 Crear `features/finanzas/types/index.ts` — tipos compartidos (LiquidacionPeriodo, LiquidacionEntry, SalarioBase, Plus, Factura, FacturaFilters, etc.)
- [x] 1.3 Crear servicios HTTP: `liquidaciones.ts`, `salarios.ts`, `facturas.ts`

## 2. Setup — Módulo Admin

- [x] 2.1 Crear estructura `features/admin/` con subdirectorios: components, hooks, pages, services, types
- [x] 2.2 Crear `features/admin/types/index.ts` — tipos compartidos (Carrera, Cohorte, UsuarioTenant, AuditoriaEntry, AuditoriaFilters, etc.)
- [x] 2.3 Crear servicios HTTP: `estructura.ts`, `usuarios.ts`, `auditoria.ts`

## 3. Liquidaciones del período

- [x] 3.1 Crear `features/finanzas/pages/LiquidacionesPeriodo.tsx` — layout con filtros (cohorte, mes), 3 tabs (General/NEXO/Factura) y KPIs de cabecera
- [x] 3.2 Crear `features/finanzas/components/LiquidacionTable.tsx` — tabla con columnas: docente, rol, materias, salario base, plus, total; fila expandible con detalle
- [x] 3.3 Crear `features/finanzas/components/LiquidacionKpiCards.tsx` — cards de "Total sin factura" y "Total con factura"
- [x] 3.4 Crear `features/finanzas/components/CerrarLiquidacionModal.tsx` — modal de confirmación con advertencia de irreversibilidad
- [x] 3.5 Agregar ruta `/liquidaciones` con guard `liquidaciones:ver`

## 4. Historial de liquidaciones

- [x] 4.1 Crear `features/finanzas/pages/HistorialLiquidaciones.tsx` — tabla de liquidaciones cerradas con filtros cohorte/mes
- [x] 4.2 Implementar navegación desde historial a detalle de liquidación (modo solo lectura)
- [x] 4.3 Agregar ruta `/liquidaciones/historial` con guard `liquidaciones:ver`

## 5. Grilla salarial

- [x] 5.1 Crear `features/finanzas/pages/GestionSalarios.tsx` — layout con 2 tabs: Salarios Base y Plus
- [x] 5.2 Crear `features/finanzas/components/SalarioBaseForm.tsx` — formulario con rol, monto, vigencia desde/hasta
- [x] 5.3 Crear `features/finanzas/components/PlusForm.tsx` — formulario con clave, rol, descripción, monto/porcentaje, vigencia
- [x] 5.4 Implementar validación de solapamiento de vigencias para plus (error desde backend)
- [x] 5.5 Agregar ruta `/salarios` con guard `liquidaciones:configurar-salarios`

## 6. Gestión de facturas

- [x] 6.1 Crear `features/finanzas/pages/GestionFacturas.tsx` — tabla de facturas con filtros (docente, estado, rango fechas, búsqueda)
- [x] 6.2 Crear `features/finanzas/components/FacturaDetalle.tsx` — expansión de fila con detalle completo (fecha carga, período, archivo, datos de pago)
- [x] 6.3 Implementar cambio de estado pendiente/abonada con confirmación
- [x] 6.4 Agregar ruta `/facturas` con guard `liquidaciones:ver`

## 7. Estructura académica (Admin)

- [x] 7.1 Crear `features/admin/pages/EstructuraAcademica.tsx` — layout con 2 tabs: Carreras y Cohortes
- [x] 7.2 Crear `features/admin/components/CarreraForm.tsx` — formulario ABM con código, nombre, estado (activa/inactiva)
- [x] 7.3 Crear `features/admin/components/CohorteForm.tsx` — formulario ABM con nombre, año inicio, vigencia desde/hasta, estado
- [x] 7.4 Implementar validación de vigencias de cohorte (desde < hasta)
- [x] 7.5 Agregar ruta `/estructura` con guard `estructura:gestionar`

## 8. Usuarios del tenant

- [x] 8.1 Crear `features/admin/pages/GestionUsuarios.tsx` — tabla de usuarios con filtros por rol y búsqueda
- [x] 8.2 Crear `features/admin/components/UsuarioForm.tsx` — formulario alta/edición con: nombre, email, identificación fiscal, roles, banco, CBU/alias, regional, modalidad facturación
- [x] 8.3 Implementar enmascaramiento de CBU con opción "Revelar" temporal (30s)
- [x] 8.4 Implementar activación/desactivación de usuario
- [x] 8.5 Agregar ruta `/usuarios` con guard `usuarios:gestionar`

## 9. Panel de auditoría y métricas

- [x] 9.1 Crear `features/admin/pages/PanelAuditoria.tsx` — layout con barra de filtros persistente y 4 sub-vistas
- [x] 9.2 Crear `features/admin/components/AuditoriaAccionesPorDia.tsx` — gráfico de barras CSS con volumen por día
- [x] 9.3 Crear `features/admin/components/AuditoriaEstadoComunicaciones.tsx` — tabla con distribución de estados por docente/materia
- [x] 9.4 Crear `features/admin/components/AuditoriaInteracciones.tsx` — tabla con métricas de uso por docente/materia
- [x] 9.5 Crear `features/admin/components/AuditoriaUltimasAcciones.tsx` — tabla con últimos 200 registros del log
- [x] 9.6 Agregar ruta `/auditoria` con guard `auditoria:ver`

## 10. Log completo de auditoría

- [x] 10.1 Crear `features/admin/pages/LogAuditoria.tsx` — tabla paginada con todas las columnas del log
- [x] 10.2 Implementar filtros avanzados: rango fechas, materia, usuario, tipo de acción, IP
- [x] 10.3 Implementar ordenamiento por columnas y limpieza de filtros
- [x] 10.4 Agregar ruta `/auditoria/log` con guard `auditoria:ver`

## 11. Navegación e integración

- [x] 11.1 Agregar sección "Finanzas" en sidebar con dropdown: Liquidaciones, Historial, Salarios, Facturas
- [x] 11.2 Agregar sección "Administración" en sidebar con dropdown: Estructura, Usuarios, Auditoría, Log
- [x] 11.3 Conectar invalidación de queries entre módulos relacionados (cierre de liquidación → invalidar historial)

## 12. Tests — Finanzas

- [x] 12.1 Tests de Liquidaciones: vista segmentada (3 tabs), KPIs, filtros por cohorte/mes/docente
- [x] 12.2 Tests de Cierre de liquidación: modal de confirmación, guard de permiso `liquidaciones:cerrar`
- [x] 12.3 Tests de Grilla salarial: ABM salarios base, ABM plus, validación de solapamiento
- [x] 12.4 Tests de Gestión de facturas: filtros, cambio de estado pendiente/abonada, detalle expandible

## 13. Tests — Admin

- [x] 13.1 Tests de Estructura académica: ABM carreras (alta/edición/desactivar), ABM cohortes (alta/edición/cerrar), validación vigencias
- [x] 13.2 Tests de Usuarios: alta con datos bancarios, edición de roles, activar/desactivar, enmascaramiento CBU
- [x] 13.3 Tests de Panel de auditoría: 4 sub-vistas, filtros persistentes al cambiar vista, gráfico de barras
- [x] 13.4 Tests de Log de auditoría: paginación, filtros combinados, ordenamiento, limpiar filtros

## 14. Tests — Integración

- [x] 14.1 Test de integración Finanzas: flujo completo ver liquidación → cerrar → ver en historial
- [x] 14.2 Test de integración Admin: flujo crear carrera → crear cohorte → crear usuario y asignar
- [x] 14.3 Test de guards de permiso: rutas de FINANZAS requieren rol FINANZAS/ADMIN, rutas de ADMIN requieren rol ADMIN
