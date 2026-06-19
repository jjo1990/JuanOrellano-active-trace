## ADDED Requirements

### Requirement: Preview de comunicación a atrasados
El sistema SHALL mostrar una vista previa del mensaje que se enviará a los alumnos atrasados, incluyendo variables de sustitución resueltas.

#### Scenario: Preview con destinatarios
- **WHEN** el usuario selecciona alumnos atrasados, elige una plantilla y hace clic en "Previsualizar"
- **THEN** el sistema muestra el mensaje con variables sustituidas (nombre, materia, actividades pendientes) y la lista de destinatarios.

#### Scenario: Preview sin destinatarios seleccionados
- **WHEN** el usuario hace clic en "Previsualizar" sin seleccionar ningún alumno
- **THEN** el sistema muestra error "Seleccioná al menos un destinatario".

### Requirement: Envío de comunicación
El sistema SHALL permitir encolar el envío de comunicaciones a los destinatarios seleccionados y mostrar el tracking de estado en tiempo real.

#### Scenario: Envío exitoso
- **WHEN** el usuario confirma el envío después del preview
- **THEN** el sistema encola los mensajes, muestra un indicador de progreso con estados Pendiente → Enviando → Enviado, y actualiza automáticamente cada 5 segundos.

#### Scenario: Error en envío
- **WHEN** un mensaje falla durante el envío
- **THEN** el sistema muestra el estado "Error" para ese destinatario con un tooltip del motivo, sin interrumpir los demás envíos.

### Requirement: Historial de comunicaciones
El sistema SHALL mostrar el historial de comunicaciones enviadas para la materia actual.

#### Scenario: Historial con envíos previos
- **WHEN** el usuario accede a la pestaña "Historial" de comunicación
- **THEN** el sistema muestra una tabla con: Fecha, Destinatarios, Estado general, Acciones (ver detalle).
