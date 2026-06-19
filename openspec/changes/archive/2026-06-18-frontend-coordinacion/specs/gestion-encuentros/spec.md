## ADDED Requirements

### Requirement: Crear encuentro recurrente
El sistema SHALL permitir crear un slot de encuentro recurrente que genere instancias automáticamente por cantidad de semanas.

#### Scenario: Crear encuentro semanal
- **WHEN** el usuario define día, hora, meet_url, cantidad de semanas=16 y confirma
- **THEN** el sistema crea el slot y genera 16 instancias, mostrando la lista generada.

### Requirement: Editar instancia de encuentro
El sistema SHALL permitir modificar una instancia individual: estado (Programada/Realizada/Cancelada), meet_url, video_url, comentario.

#### Scenario: Marcar instancia como realizada
- **WHEN** el usuario cambia el estado de una instancia a "Realizada" y agrega video_url
- **THEN** el sistema actualiza la instancia y refleja el cambio en el calendario.

### Requirement: Registro de guardias
El sistema SHALL permitir al TUTOR registrar una guardia y al COORDINADOR consultar el listado global con export.

#### Scenario: Registrar guardia
- **WHEN** un TUTOR completa el formulario de guardia (fecha, materia, docente cubierto, comentario)
- **THEN** el sistema registra la guardia.

#### Scenario: Coordinador consulta guardias
- **WHEN** el COORDINADOR accede a la vista de guardias y filtra por fecha
- **THEN** el sistema muestra todas las guardias del tenant y permite exportar.
