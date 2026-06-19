## Context

C-22 es el primer feature module productivo del frontend, construido sobre el shell de C-21. El backend ya expone todos los endpoints necesarios (C-10, C-11, C-12). El frontend actual tiene solo el módulo `auth` (login, 2FA, recuperación) y la infraestructura compartida (`shared/`).

**Stack frontend**: React 19 + TypeScript + Vite, TanStack Query v5, React Hook Form + Zod, Tailwind CSS, Axios. Feature-based modules bajo `features/{name}/{components,hooks,pages,services,types}`. Shared components en `shared/components/`.

**APIs consumidas**:
- `POST /api/calificaciones/importar` — subir archivo, preview, confirmar
- `GET /api/calificaciones` — listado por materia
- `PUT /api/umbrales/{materia_id}` — configurar umbral
- `GET /api/analisis/atrasados` — alumnos atrasados
- `GET /api/analisis/ranking` — ranking de aprobadas
- `GET /api/analisis/notas-finales` — notas agrupadas
- `GET /api/analisis/tps-sin-corregir` — TPs pendientes
- `POST /api/comunicaciones/preview` — preview de mensaje
- `POST /api/comunicaciones/enviar` — encolar envío
- `GET /api/comunicaciones/estado/{lote_id}` — tracking
- `GET /api/analisis/monitor` — monitor de seguimiento

## Goals / Non-Goals

**Goals:**
- Página de importación de calificaciones con upload + preview + selección de actividades
- Página de configuración de umbral por materia
- Dashboard de materia con atrasados, ranking, notas finales, TPs sin corregir
- Página de comunicación a atrasados con preview, envío y tracking
- Monitor de seguimiento filtrable para tutor/profesor
- Navegación integrada en el layout existente con guards de permiso

**Non-Goals:**
- Vista de COORDINADOR/ADMIN (eso es C-23)
- Gestión de padrón de alumnos (C-23)
- Panel de métricas/auditoría (C-24)
- Diseño responsive mobile-first (se asume desktop)
- Tests E2E con Playwright (solo tests de componente)

## Decisions

### D1: Una sola feature `academico` con sub-rutas por función

**Alternativa**: features separadas (`import`, `analisis`, `comunicacion`).

**Decisión**: un solo módulo `features/academico/` con páginas organizadas por función. Comparten tipos, hooks y servicios.

**Razón**: todas las páginas operan sobre el mismo dominio (gestión de comisión del docente). Separarlas duplicaría tipos y hooks compartidos. La navegación entre importar → analizar → comunicar es un flujo continuo.

### D2: TanStack Query con invalidación en cascada

Cuando se importan calificaciones, se invalidan queries de análisis (atrasados, ranking, notas). Cuando se envía una comunicación, se invalida el tracking.

**Decisión**: usar `queryClient.invalidateQueries` con prefixes (`['calificaciones']`, `['analisis']`, `['comunicaciones']`) después de cada mutación exitosa.

### D3: File upload con preview usando FormData

El endpoint de importación acepta `multipart/form-data`. El preview se obtiene con una request preliminar (`?preview=true`) o el backend devuelve preview en la response del POST.

**Decisión**: upload en dos pasos — POST con archivo para obtener preview, luego POST de confirmación con actividades seleccionadas. El estado del wizard (archivo, preview, selección) se maneja con React Hook Form.

### D4: Componentes de tabla con ordenamiento client-side

Para datasets de tamaño moderado (< 500 filas, típico en una materia), el ordenamiento y filtrado se hace en el cliente.

**Decisión**: componente `DataTable` genérico con props: `columns`, `data`, `sortable`, `filterable`. Usa `useMemo` para ordenar/filtrar. Si escala, se migra a server-side.

### D5: Tracking de comunicación con polling

El estado de envío de comunicaciones (Pendiente → Enviando → Enviado/Error) se actualiza mediante polling cada 5 segundos.

**Decisión**: `useQuery` con `refetchInterval: 5000` y `enabled: !!loteId`. Sin WebSockets — YAGNI para este módulo.

### D6: Guards de permiso en rutas

Cada ruta declara el permiso requerido usando el mismo sistema de C-21 (basado en los claims del JWT).

**Decisión**: wrapper `RequirePermission` alrededor de cada página, declarando el permiso necesario (`calificaciones:importar`, `atrasados:ver`, `comunicacion:enviar`).

## Risks / Trade-offs

- **[Riesgo] Preview de archivo grande congela la UI**: archivos de calificaciones con muchos alumnos/actividades pueden ser lentos de parsear. → **Mitigación**: el parsing lo hace el backend; el frontend solo muestra la respuesta. Agregar spinner y mensaje de carga.
- **[Trade-off] Polling vs WebSockets para tracking**: polling cada 5s es simple pero genera tráfico innecesario. → **Aceptado**: para el volumen esperado (decenas de envíos, no miles), polling es suficiente.
- **[Riesgo] UX del wizard de importación**: si el usuario recarga la página pierde el estado del wizard. → **Mitigación**: guardar archivo en sessionStorage temporalmente (o el backend lo retiene con un token de upload).
