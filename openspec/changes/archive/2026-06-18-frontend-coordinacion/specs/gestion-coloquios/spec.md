## ADDED Requirements

### Requirement: Crear convocatoria de coloquio
El sistema SHALL permitir crear una convocatoria con materia, días disponibles, horarios y cupos.

#### Scenario: Crear convocatoria con turnos
- **WHEN** el usuario define materia, días=[Lun, Mar], cupo=5 por turno y confirma
- **THEN** el sistema crea la convocatoria con la cantidad de turnos especificada.

### Requirement: Importar alumnos a convocatoria
El sistema SHALL permitir importar alumnos desde el padrón de la materia a la convocatoria.

#### Scenario: Importar alumnos
- **WHEN** el usuario hace clic en "Importar alumnos" en una convocatoria
- **THEN** el sistema carga los alumnos del padrón de la materia y los asocia a la convocatoria.

### Requirement: Panel de métricas de coloquios
El sistema SHALL mostrar métricas agregadas: total convocados, reservas confirmadas, turnos libres.

#### Scenario: Ver métricas
- **WHEN** el usuario accede al panel de coloquios
- **THEN** el sistema muestra cards con: Convocados, Reservas, Libres, % Ocupación.

### Requirement: Vista de reservas por turno
El sistema SHALL permitir al COORDINADOR ver las reservas de cada turno.

#### Scenario: Ver reservas de un turno
- **WHEN** el usuario expande un turno en la grilla
- **THEN** el sistema muestra los alumnos que reservaron ese turno.
