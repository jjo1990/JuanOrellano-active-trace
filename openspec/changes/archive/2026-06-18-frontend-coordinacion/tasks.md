## 1. Setup

- [x] 1.1 Crear estructura `features/coordinacion/` con subdirectorios: components, hooks, pages, services, types
- [x] 1.2 Crear `features/coordinacion/types/index.ts` — tipos compartidos (Equipo, Aviso, Tarea, Encuentro, Coloquio, Programa, FechaAcademica, etc.)
- [x] 1.3 Crear servicios HTTP: `equipos.ts`, `avisos.ts`, `tareas.ts`, `monitores.ts`, `encuentros.ts`, `coloquios.ts`, `programas.ts`

## 2. Gestión de equipos

- [x] 2.1 Crear `pages/GestionEquipos.tsx` — layout con tabs: Mis Equipos, Asignar, Historial
- [x] 2.2 Crear `components/EquiposTable.tsx` — tabla de equipo con filtros cohorte/materia
- [x] 2.3 Crear `components/AsignacionMasiva.tsx` — búsqueda asincrónica + selección múltiple + chips
- [x] 2.4 Crear `components/ClonarEquipo.tsx` — selector cohorte origen/destino + confirmación
- [x] 2.5 Agregar ruta `/equipos` con guard `equipos:asignar`

## 3. Gestión de avisos

- [x] 3.1 Crear `pages/GestionAvisos.tsx` — tabla de avisos + botón crear
- [x] 3.2 Crear `components/AvisoForm.tsx` — formulario con scope, severidad, vigencia, requiere_ack
- [x] 3.3 Crear `components/AvisoAcknowledgments.tsx` — vista de confirmaciones por aviso
- [x] 3.4 Agregar ruta `/avisos` con guard `avisos:publicar`

## 4. Gestión de tareas

- [x] 4.1 Crear `pages/GestionTareas.tsx` — layout con tabs: Mis Tareas, Administración
- [x] 4.2 Crear `components/TareaForm.tsx` — formulario crear/editar con asignado_a y comentario
- [x] 4.3 Crear `components/TareaWorkflow.tsx` — botones de cambio de estado + comentario
- [x] 4.4 Agregar ruta `/tareas` con guard `tareas:gestionar`

## 5. Monitores transversales

- [x] 5.1 Crear `pages/MonitoresTransversales.tsx` — layout con tabs: General, Por Docente
- [x] 5.2 Crear `components/MonitorGeneralTable.tsx` — filtros avanzados + DataTable + export
- [x] 5.3 Crear `components/MonitorPorDocente.tsx` — selector de docente + tabla de sus alumnos
- [x] 5.4 Agregar ruta `/monitores` con guard `atrasados:ver`

## 6. Gestión de encuentros

- [x] 6.1 Crear `pages/GestionEncuentros.tsx` — layout con tabs: Calendario, Guardias
- [x] 6.2 Crear `components/EncuentroForm.tsx` — formulario recurrente/único con cantidad de semanas
- [x] 6.3 Crear `components/CalendarioEncuentros.tsx` — vista mensual simple con instancias
- [x] 6.4 Crear `components/InstanciaEditor.tsx` — modal editar estado/meet_url/video_url/comentario
- [x] 6.5 Crear `components/GuardiasTable.tsx` — tabla de guardias con filtro fecha + export
- [x] 6.6 Agregar ruta `/encuentros` con guard `encuentros:gestionar`

## 7. Gestión de coloquios

- [x] 7.1 Crear `pages/GestionColoquios.tsx` — layout con tabs: Convocatorias, Métricas
- [x] 7.2 Crear `components/ConvocatoriaForm.tsx` — formulario con días, cupos, materia
- [x] 7.3 Crear `components/ReservasTurno.tsx` — grilla expandible de turnos con reservas
- [x] 7.4 Crear `components/MetricasColoquios.tsx` — cards con KPIs
- [x] 7.5 Agregar ruta `/coloquios` con guard `coloquios:gestionar`

## 8. Programas y fechas

- [x] 8.1 Crear `pages/GestionProgramas.tsx` — upload + asociar + tabla
- [x] 8.2 Crear `components/FechasAcademicasTable.tsx` — ABM de fechas con filtro cohorte
- [x] 8.3 Agregar ruta `/programas` con guard `estructura:gestionar`

## 9. Setup de cuatrimestre

- [x] 9.1 Crear `pages/SetupCuatrimestre.tsx` — wizard con stepper de 5 pasos
- [x] 9.2 Crear componente para cada paso: CohorteSelector, DocentesAsignacion, PadronImport, FechasConfig, ConfirmacionResumen
- [x] 9.3 Implementar persistencia en sessionStorage para guardar progreso
- [x] 9.4 Agregar ruta `/setup` con guard `equipos:asignar`

## 10. Navegación e integración

- [x] 10.1 Agregar sección "Coordinación" en sidebar con dropdown de todos los módulos
- [x] 10.2 Conectar invalidación de queries entre módulos relacionados

## 11. Tests

- [x] 11.1 Tests de Equipos: asignación masiva, clonar, export
- [x] 11.2 Tests de Avisos: ABM, filtro por scope, acknowledgments
- [x] 11.3 Tests de Tareas: workflow de estados, delegación
- [x] 11.4 Tests de Monitores: filtros, búsqueda con debounce, export
- [x] 11.5 Tests de Encuentros: creación recurrente, edición instancia
- [x] 11.6 Tests de Coloquios: convocatoria, métricas
- [x] 11.7 Tests de Setup: navegación del wizard, persistencia sessionStorage
