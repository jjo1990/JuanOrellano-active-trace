## ADDED Requirements

### Requirement: Avisos visibles para el usuario
El sistema SHALL mostrar a cada usuario solo los avisos que coinciden con su audiencia según RN-20, dentro de la ventana de vigencia RN-18 y ordenados por prioridad (F3.5 lectura).

#### Scenario: PROFESOR ve avisos de su materia
- **WHEN** un PROFESOR asignado a materia X envía `GET /api/avisos/visibles`
- **THEN** el sistema devuelve avisos globales + avisos de materia X + avisos con rol_destino=PROFESOR, todos activos y dentro de ventana de vigencia

#### Scenario: Aviso fuera de ventana no se muestra (RN-18)
- **WHEN** un aviso tiene fin_en anterior a now()
- **THEN** no aparece en `GET /api/avisos/visibles`

#### Scenario: Aviso inactivo no se muestra
- **WHEN** un aviso tiene activo=false
- **THEN** no aparece en `GET /api/avisos/visibles` aunque esté en ventana

#### Scenario: ALUMNO ve avisos globales
- **WHEN** un ALUMNO consulta avisos visibles
- **THEN** ve avisos con alcance=Global y avisos con rol_destino=ALUMNO que estén activos y en ventana

#### Scenario: Avisos ordenados por prioridad
- **WHEN** hay múltiples avisos visibles
- **THEN** se ordenan por orden ASC (menor número = mayor prioridad), luego por inicio_en DESC

### Requirement: Detalle de aviso
El sistema SHALL permitir ver el detalle completo de un aviso visible.

#### Scenario: Usuario ve detalle de aviso visible
- **WHEN** un usuario envía `GET /api/avisos/{id}` de un aviso que le es visible
- **THEN** el sistema devuelve el aviso con cuerpo completo

#### Scenario: Usuario no ve aviso fuera de su audiencia
- **WHEN** un PROFESOR intenta ver un aviso segmentado para ALUMNO
- **THEN** el sistema responde 404 (no revela existencia)
