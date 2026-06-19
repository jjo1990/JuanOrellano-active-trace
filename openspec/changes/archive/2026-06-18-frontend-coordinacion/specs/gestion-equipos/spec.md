## ADDED Requirements

### Requirement: Vista mis-equipos
El sistema SHALL mostrar al COORDINADOR una vista de los equipos docentes con filtro por cohorte y materia.

#### Scenario: Ver equipos de una cohorte
- **WHEN** el usuario selecciona una cohorte activa
- **THEN** el sistema muestra tabla con columnas: Docente, Rol, Materia, Comisión, Vigencia, Acciones.

### Requirement: Asignación masiva de docentes
El sistema SHALL permitir asignar múltiples docentes a materias/roles en un solo paso con búsqueda asincrónica.

#### Scenario: Asignar docentes en lote
- **WHEN** el usuario busca docentes por nombre, los selecciona, elige rol y materia, define vigencia y confirma
- **THEN** el sistema crea las asignaciones y muestra confirmación con cantidad.

### Requirement: Clonar equipo entre períodos
El sistema SHALL permitir duplicar las asignaciones vigentes de una cohorte a otra con nuevas fechas.

#### Scenario: Clonar a nuevo período
- **WHEN** el usuario selecciona cohorte origen y destino, y confirma clonado
- **THEN** el sistema crea copias de las asignaciones con fechas del nuevo período y muestra resumen.

### Requirement: Exportar equipo
El sistema SHALL permitir exportar el equipo docente actual a un archivo descargable.

#### Scenario: Exportar equipo
- **WHEN** el usuario hace clic en "Exportar"
- **THEN** el sistema descarga un archivo .xlsx con los datos del equipo.
