## ADDED Requirements

### Requirement: Log completo de auditoría
El sistema SHALL mostrar el log completo de auditoría con todos los campos registrados: fecha y hora, identificador de usuario, materia, tipo de acción, cantidad de registros afectados, dirección IP de origen y agente de usuario.

#### Scenario: Ver log completo con paginación
- **WHEN** el usuario ADMIN accede al log completo de auditoría
- **THEN** el sistema muestra una tabla paginada con todas las acciones registradas en orden cronológico inverso.

#### Scenario: Navegar páginas del log
- **WHEN** el usuario hace clic en "Siguiente" al final de la página actual
- **THEN** el sistema carga la página siguiente de registros manteniendo los filtros activos.

### Requirement: Filtros avanzados del log
El sistema SHALL permitir filtrar el log por: rango de fechas, materia, usuario, tipo de acción y dirección IP.

#### Scenario: Filtrar por tipo de acción
- **WHEN** el usuario selecciona "importación" en el filtro de tipo de acción
- **THEN** el sistema muestra solo los registros cuyo tipo de acción es importación.

#### Scenario: Combinar filtros
- **WHEN** el usuario selecciona un rango de fechas, una materia y un usuario específico simultáneamente
- **THEN** el sistema muestra solo los registros que cumplen todos los criterios combinados.

#### Scenario: Limpiar filtros
- **WHEN** el usuario hace clic en "Limpiar filtros"
- **THEN** el sistema remueve todos los filtros aplicados y recarga el log sin restricciones.

### Requirement: Ordenamiento de columnas del log
El sistema SHALL permitir ordenar la tabla del log por cualquiera de sus columnas visibles.

#### Scenario: Ordenar por fecha
- **WHEN** el usuario hace clic en el encabezado de la columna "Fecha"
- **THEN** el sistema reordena la tabla por fecha (alternando ascendente/descendente en cada clic).
