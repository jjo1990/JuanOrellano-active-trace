## ADDED Requirements

### Requirement: Monitor general de actividades
El sistema SHALL mostrar una vista transversal de todos los alumnos del tenant con filtros avanzados y exportación.

#### Scenario: Filtrar por materia y regional
- **WHEN** el usuario selecciona una materia y una regional en los filtros
- **THEN** el sistema muestra solo los alumnos que coinciden, con columnas: Alumno, Email, Comisión, Actividades completadas, Estado.

#### Scenario: Exportar datos del monitor
- **WHEN** el usuario aplica filtros y hace clic en "Exportar"
- **THEN** el sistema descarga un archivo .xlsx con los datos filtrados.

### Requirement: Monitor de seguimiento por docente
El sistema SHALL permitir al COORDINADOR ver el estado de actividades de los alumnos asignados a un docente específico.

#### Scenario: Filtrar por docente
- **WHEN** el usuario selecciona un docente en el filtro
- **THEN** el sistema muestra solo los alumnos de las comisiones de ese docente.

### Requirement: Búsqueda libre con debounce
El sistema SHALL implementar búsqueda por nombre de alumno con debounce de 300ms para evitar requests excesivos.

#### Scenario: Búsqueda con debounce
- **WHEN** el usuario escribe "Mar" en el campo de búsqueda
- **THEN** el sistema espera 300ms después de la última tecla antes de ejecutar la query.
