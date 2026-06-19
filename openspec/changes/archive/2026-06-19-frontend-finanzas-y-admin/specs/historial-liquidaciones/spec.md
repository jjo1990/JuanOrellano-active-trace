## ADDED Requirements

### Requirement: Consulta de historial de liquidaciones
El sistema SHALL permitir consultar liquidaciones de períodos anteriores que ya fueron cerradas, con filtros por cohorte y mes.

#### Scenario: Ver historial filtrado
- **WHEN** el usuario accede al historial de liquidaciones y selecciona una cohorte
- **THEN** el sistema muestra una tabla con las liquidaciones cerradas de esa cohorte: período (mes/año), fecha de cierre, total liquidado, cantidad de docentes.

#### Scenario: Ver detalle de liquidación histórica
- **WHEN** el usuario hace clic en una liquidación del historial
- **THEN** el sistema muestra la misma vista segmentada (General/NEXO/Factura) de esa liquidación en modo solo lectura, sin botón de cierre.

#### Scenario: Historial vacío
- **WHEN** no hay liquidaciones cerradas para los filtros seleccionados
- **THEN** el sistema muestra un mensaje "No hay liquidaciones cerradas para este período".
