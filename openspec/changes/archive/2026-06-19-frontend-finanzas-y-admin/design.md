## Context

C-24 es el último módulo frontend — agrupa dos dominios distintos (FINANZAS y ADMIN) en un solo change porque comparten el perfil de governance BAJO y sus backends ya están completos y testeados. Son 8 capacidades sobre 4 APIs backend existentes (C-06 estructura, C-07 usuarios, C-18 liquidaciones, C-19 auditoría). El frontend ya tiene el shell (C-21), el módulo academico (C-22) y el módulo coordinacion (C-23). Se reusan DataTable, StatusBadge y RequirePermission.

## Goals / Non-Goals

**Goals:**
- 2 feature modules: `finanzas` (5 capacidades) y `admin` (3 capacidades)
- Vista de liquidaciones con segmentación en 3 tabs (general / NEXO / factura) + KPIs de totales
- Cierre de liquidación con confirmación explícita del usuario
- ABM de grilla salarial (salarios base + plus) con vigencia temporal
- ABM de facturas con cambio de estado pendiente/abonada
- ABM de estructura académica (carreras, cohortes) con cambio de estado activa/inactiva
- ABM de usuarios del tenant con datos completos
- Panel de auditoría con 4 sub-vistas (acciones por día, estado comunicaciones, interacciones, log reciente)
- Log completo de auditoría con filtros avanzados
- Menús "Finanzas" y "Administración" en sidebar con dropdowns
- Guards de permiso FINANZAS y ADMIN en todas las rutas

**Non-Goals:**
- Lógica de cálculo de plus (es backend, C-18)
- Integración con pasarelas de pago
- Generación de PDF de liquidación (exportación a Excel/CSV desde la tabla)
- Configuración de tenant (infraestructura)

## Decisions

### D1: Dos feature modules separados: `finanzas` y `admin`
Cada dominio tiene su propio feature module con estructura completa (components, hooks, pages, services, types). No comparten estado ni queries entre sí — son dominios independientes. Esto mantiene el patrón de feature-based modules de C-22 y C-23.

### D2: Vista de liquidaciones con 3 tabs: General / NEXO / Factura
Una sola página `LiquidacionesPeriodo` con 3 tabs internos que filtran los mismos datos por segmento. Cada tab muestra una DataTable con la misma estructura (docente, rol, materias, base, plus, total) pero datos filtrados según segmento. KPIs de cabecera siempre visibles (total sin factura, total con factura).

### D3: Cierre de liquidación con modal de confirmación
Antes de ejecutar el cierre (acción irreversible), un modal requiere confirmación explícita con mensaje de advertencia. El botón de cierre solo aparece si el usuario tiene permiso `liquidaciones:cerrar`.

### D4: Grilla salarial con dos sub-tabs: Salarios Base y Plus
Dentro de `GestionSalarios`, dos tabs manejan independientemente las tablas de salario base (por rol) y plus (por clave + rol + descripción). Ambas comparten el patrón: tabla con vigencia desde/hasta, botón agregar, editar inline en la fila.

### D5: Filtros de panel de auditoría como barra superior persistente
Una barra de filtros (rango de fechas, materia, usuario, estado) aplica a las 4 sub-vistas del panel. Los filtros se mantienen al cambiar de sub-vista mediante estado local compartido en la página.

### D6: Log de auditoría con paginación server-side
El log completo usa paginación (cursor o page-based) desde el backend. Los filtros se envían como query params. Máximo configurable por defecto de 200 registros visibles por página.

## Risks / Trade-offs

- **[Riesgo] Segmentación NEXO vs factura depende de datos correctos en backend**: Si los flags de facturación no están bien poblados, la segmentación muestra datos incorrectos. → **Mitigación**: el backend (C-18) ya maneja esta lógica — el frontend solo consume.
- **[Riesgo] Cierre de liquidación irreversible**: Una vez cerrada no se puede modificar. → **Mitigación**: modal de confirmación con doble verificación (texto de advertencia + botón "Confirmar cierre").
- **[Trade-off] Dos feature modules vs uno solo**: Separar `finanzas` de `admin` duplica estructura de directorios pero mantiene cohesión de dominio y facilita code splitting por rol. → **Aceptado**: cada módulo es independiente y solo carga si el usuario tiene los permisos correspondientes.
- **[Trade-off] Calendario de acciones por día simple**: No se usa librería de gráficos para el panel de auditoría — se implementa con barras CSS puras para mantener cero dependencias externas. → **Aceptado**: suficiente para la Fase 1 del producto.
