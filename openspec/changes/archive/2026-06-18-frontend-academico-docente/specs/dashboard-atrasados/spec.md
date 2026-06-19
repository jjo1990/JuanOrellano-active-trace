## ADDED Requirements

### Requirement: Vista de alumnos atrasados
El sistema SHALL mostrar una tabla de alumnos con actividades faltantes o nota inferior al umbral configurado.

#### Scenario: Dashboard con atrasados
- **WHEN** el usuario accede al dashboard de una materia con datos importados
- **THEN** el sistema muestra una tabla con columnas: Alumno, Actividades pendientes, Nota promedio, Estado (Atrasado / Al día).

#### Scenario: Dashboard sin datos
- **WHEN** el usuario accede al dashboard de una materia sin calificaciones importadas
- **THEN** el sistema muestra un estado vacío: "No hay datos importados. Importá calificaciones para ver el análisis."

### Requirement: Ranking de actividades aprobadas
El sistema SHALL mostrar una tabla ordenada por cantidad de actividades aprobadas por alumno, incluyendo solo alumnos con al menos una actividad aprobada.

#### Scenario: Ranking con datos
- **WHEN** hay alumnos con actividades aprobadas
- **THEN** el sistema muestra una tabla ordenada descendente por "Aprobadas", con columnas: Alumno, Aprobadas, Promedio.

### Requirement: Notas finales agrupadas
El sistema SHALL mostrar una tabla de notas finales calculadas por alumno, agrupando las actividades configuradas.

#### Scenario: Notas finales
- **WHEN** el usuario selecciona la pestaña "Notas Finales"
- **THEN** el sistema muestra una tabla con columnas: Alumno, Nota Final, Estado (Aprobado / Desaprobado).

### Requirement: Exportar TPs sin corregir
El sistema SHALL permitir exportar un listado de trabajos prácticos detectados como pendientes de corrección.

#### Scenario: Exportar TPs pendientes
- **WHEN** el usuario hace clic en "Exportar TPs sin corregir"
- **THEN** el sistema descarga un archivo .xlsx con el listado de alumnos y actividades pendientes.
