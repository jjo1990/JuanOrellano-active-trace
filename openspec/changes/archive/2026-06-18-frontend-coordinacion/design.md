## Context

C-23 es el módulo frontend de coordinación — el más grande de los 3 frontends. Agrupa 8 capacidades distintas sobre 6 APIs backend existentes. El frontend ya tiene el shell (C-21), el módulo auth, y el módulo academico (C-22). Se reusan DataTable, StatusBadge y RequirePermission de C-22.

## Goals / Non-Goals

**Goals:**
- 8 páginas de coordinación consumiendo APIs existentes
- Flujo guiado de setup de cuatrimestre (wizard multi-paso)
- Menú "Coordinación" en sidebar con dropdown
- Guards de permiso COORDINADOR/ADMIN en todas las rutas

**Non-Goals:**
- Vista de FINANZAS (C-24)
- Vista de ADMIN de estructura académica (C-24)
- Panel de auditoría y métricas (C-24)
- Integración con calendario externo

## Decisions

### D1: Feature module `coordinacion` con sub-módulos por dominio
Cada capacidad tiene su propia carpeta de componentes y página, compartiendo tipos y servicios a nivel feature.

### D2: Setup de cuatrimestre como wizard de 5 pasos
1. Crear/Seleccionar Cohorte → 2. Asignar Docentes (masiva) → 3. Importar Padrón → 4. Definir Fechas Académicas → 5. Revisar y Confirmar. Estado del wizard en React Hook Form con persistencia en sessionStorage.

### D3: Asignación masiva con búsqueda asincrónica
Componente de búsqueda con autocompletado que consulta al backend por nombre/apellido. Selección múltiple con chips removibles.

### D4: Calendario de encuentros con vista mensual
Componente de calendario simple (sin dependencia externa) para visualizar instancias de encuentros por mes. Click en día muestra detalle.

### D5: Monitores con filtros avanzados
Filtros: materia, regional, comisión, estado, búsqueda libre. Queries con debounce de 300ms. Exportación de resultados visibles.

## Risks / Trade-offs

- **[Riesgo] Complejidad del wizard de setup**: 5 pasos con dependencias entre sí (docentes antes de padrón). → **Mitigación**: validación por paso, indicador de progreso, botón "Guardar y continuar después".
- **[Trade-off] Calendario custom vs librería**: implementación propia simple vs dependencia externa. → **Aceptado**: para la Fase 1, calendario mensual simple sin drag & drop.
