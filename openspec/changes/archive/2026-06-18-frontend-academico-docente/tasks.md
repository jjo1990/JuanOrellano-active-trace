## 1. Setup del módulo

- [x] 1.1 Crear estructura `features/academico/` con subdirectorios: components, hooks, pages, services, types
- [x] 1.2 Crear `features/academico/types/index.ts` con tipos compartidos (Alumno, Actividad, Calificacion, Umbral, Comunicacion, EstadoEnvio)
- [x] 1.3 Crear `features/academico/services/calificaciones.ts` — hooks TanStack Query para endpoints de calificaciones
- [x] 1.4 Crear `features/academico/services/analisis.ts` — hooks TanStack Query para endpoints de análisis
- [x] 1.5 Crear `features/academico/services/comunicaciones.ts` — hooks TanStack Query para endpoints de comunicación

## 2. Componentes compartidos

- [x] 2.1 Crear `shared/components/DataTable.tsx` — tabla genérica con ordenamiento client-side, columnas configurables
- [x] 2.2 Crear `shared/components/StatusBadge.tsx` — badge de estado (Atrasado, Al día, Pendiente, Enviado, Error)
- [x] 2.3 Crear `shared/components/MessagePreview.tsx` — preview de mensaje con variables resueltas y lista de destinatarios

## 3. Página de importación de calificaciones

- [x] 3.1 Crear `features/academico/pages/ImportarCalificaciones.tsx` — wizard de 3 pasos: upload → preview → confirmar
- [x] 3.2 Crear componente `FileUploadStep` — selector de materia + dropzone de archivo
- [x] 3.3 Crear componente `PreviewStep` — tabla de preview con checkboxes de selección de actividades
- [x] 3.4 Crear componente `ConfirmStep` — resumen y botón de importación definitiva
- [x] 3.5 Agregar ruta `/materias/:id/importar` al router con guard `calificaciones:importar`

## 4. Página de configuración de umbral

- [x] 4.1 Crear `features/academico/pages/ConfigurarUmbral.tsx` — slider o input numérico con valor por defecto 60%
- [x] 4.2 Agregar ruta `/materias/:id/umbral` al router con guard del docente

## 5. Dashboard de materia

- [x] 5.1 Crear `features/academico/pages/DashboardMateria.tsx` — layout con tabs/pestañas
- [x] 5.2 Crear componente `AtrasadosTable.tsx` — tabla de alumnos atrasados
- [x] 5.3 Crear componente `RankingTable.tsx` — tabla de ranking de aprobadas
- [x] 5.4 Crear componente `NotasFinalesTable.tsx` — tabla de notas finales agrupadas
- [x] 5.5 Crear componente `TpsSinCorregirTable.tsx` — tabla de TPs pendientes con botón exportar
- [x] 5.6 Agregar ruta `/materias/:id/dashboard` al router con guard `atrasados:ver`

## 6. Página de comunicación a atrasados

- [x] 6.1 Crear `features/academico/pages/ComunicarAtrasados.tsx` — layout con secciones: destinatarios, preview, tracking
- [x] 6.2 Crear componente `SeleccionDestinatarios.tsx` — tabla de atrasados con checkboxes para seleccionar
- [x] 6.3 Integrar `MessagePreview` con datos reales del endpoint de preview
- [x] 6.4 Crear componente `TrackingEnvios.tsx` — polling cada 5s del estado del lote
- [x] 6.5 Crear componente `HistorialComunicaciones.tsx` — tabla de envíos anteriores
- [x] 6.6 Agregar ruta `/materias/:id/comunicar` al router con guard `comunicacion:enviar`

## 7. Monitor de seguimiento

- [x] 7.1 Crear `features/academico/pages/MonitorSeguimiento.tsx` — vista filtrable con tabla de alumnos
- [x] 7.2 Crear componente `MonitorFilters.tsx` — filtros por materia, comisión, búsqueda por alumno
- [x] 7.3 Agregar botón "Exportar" que descarga .xlsx con datos visibles
- [x] 7.4 Agregar ruta `/monitor` al router con guard `atrasados:ver`

## 8. Integración y navegación

- [x] 8.1 Agregar ítems de menú en el layout para "Mis Materias" → dropdown con importar, dashboard, umbral, comunicar
- [x] 8.2 Agregar ítem "Monitor" en el menú principal (visible para TUTOR y PROFESOR)
- [x] 8.3 Conectar invalidación de queries en cascada (importar → análisis, comunicar → tracking)
- [x] 8.4 Manejar estados de carga, error y vacío en todas las páginas

## 9. Tests

- [x] 9.1 Tests de `DataTable`: ordenamiento, filtrado, estado vacío
- [x] 9.2 Tests de `ImportarCalificaciones`: render del wizard, validación de archivo, selección de actividades
- [x] 9.3 Tests de `DashboardMateria`: tabs, tabla de atrasados, ranking, notas finales
- [x] 9.4 Tests de `ComunicarAtrasados`: selección de destinatarios, preview, tracking polling
- [x] 9.5 Tests de `MonitorSeguimiento`: filtros, búsqueda, exportación
- [x] 9.6 Tests de integración: flujo completo importar → dashboard → comunicar
