## ADDED Requirements

### Requirement: Upload de programa de materia
El sistema SHALL permitir subir un archivo (PDF/DOC) como programa de una materia, asociado a carrera y cohorte.

#### Scenario: Subir programa
- **WHEN** el usuario selecciona materia, carrera, cohorte, sube un PDF y guarda
- **THEN** el sistema asocia el programa y muestra confirmación.

### Requirement: ABM de fechas académicas
El sistema SHALL permitir crear y gestionar fechas académicas (parciales, TP, coloquios) por materia y cohorte.

#### Scenario: Crear fecha de parcial
- **WHEN** el usuario crea una fecha con tipo "Parcial", número=1, fecha, materia y cohorte
- **THEN** el sistema registra la fecha académica.

#### Scenario: Vista de calendario de fechas
- **WHEN** el usuario accede a la vista de fechas académicas de una cohorte
- **THEN** el sistema muestra tabla ordenada por fecha con columnas: Materia, Tipo, Número, Fecha.
