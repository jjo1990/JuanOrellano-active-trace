## ADDED Requirements

### Requirement: Acusar recibo de aviso
El sistema SHALL permitir a cualquier usuario confirmar la lectura de un aviso que requiere acuse (RN-19, HU-15).

#### Scenario: Usuario acusa recibo exitosamente
- **WHEN** un PROFESOR envía `POST /api/avisos/{id}/ack` para un aviso con requiere_ack=true que le es visible
- **THEN** el sistema crea un registro AcknowledgmentAviso y devuelve 200

#### Scenario: Acuse duplicado es idempotente
- **WHEN** un usuario que ya acusó recibo vuelve a enviar `POST /api/avisos/{id}/ack`
- **THEN** el sistema devuelve 200 sin crear duplicado

#### Scenario: No se puede acusar aviso fuera de audiencia
- **WHEN** un PROFESOR intenta acusar un aviso segmentado para ALUMNO
- **THEN** el sistema responde 404

#### Scenario: Aviso sin acuse requerido ignora el endpoint
- **WHEN** un usuario envía `POST /api/avisos/{id}/ack` en un aviso con requiere_ack=false
- **THEN** el sistema devuelve 200 pero no crea registro (no aplica)

### Requirement: Contadores derivados de acknowledgment
El sistema SHALL calcular contadores de vistas y acuses desde la tabla acknowledgment_aviso, sin denormalizar.

#### Scenario: COORDINADOR ve contadores en listado
- **WHEN** un COORDINADOR lista avisos con `GET /api/avisos`
- **THEN** cada aviso incluye `total_vistas` (usuarios únicos que lo vieron) y `total_acks` (usuarios que acusaron)

#### Scenario: Contador se actualiza al acusar
- **WHEN** un usuario acusa recibo de un aviso
- **THEN** el contador `total_acks` del aviso se incrementa en la siguiente consulta
