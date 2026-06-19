## ADDED Requirements

### Requirement: Monitor de seguimiento de alumnos
El sistema SHALL mostrar una vista filtrable del estado de actividades de los alumnos asignados al docente (TUTOR o PROFESOR).

#### Scenario: Vista con filtros aplicados
- **WHEN** el usuario accede al monitor y filtra por materia y comisión
- **THEN** el sistema muestra una tabla con columnas: Alumno, Email, Comisión, Actividades completadas, Estado general.

#### Scenario: Filtro por alumno específico
- **WHEN** el usuario busca por nombre de alumno en el campo de búsqueda
- **THEN** el sistema filtra la tabla mostrando solo coincidencias.

#### Scenario: Exportar datos del monitor
- **WHEN** el usuario hace clic en "Exportar"
- **THEN** el sistema descarga un archivo .xlsx con los datos visibles según los filtros aplicados.

### Requirement: Acceso restringido por rol
El sistema SHALL limitar el monitor a los alumnos que el docente tiene asignados. Un TUTOR ve solo sus tutorados; un PROFESOR ve solo sus comisiones.

#### Scenario: TUTOR ve solo sus tutorados
- **WHEN** un TUTOR accede al monitor
- **THEN** el sistema solo muestra alumnos donde el tutor tiene una asignación vigente como TUTOR.
