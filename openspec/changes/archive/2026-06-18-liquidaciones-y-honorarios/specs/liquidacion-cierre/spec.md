## ADDED Requirements

### Requirement: Cerrar liquidación del período
El sistema SHALL permitir a FINANZAS cerrar la liquidación de una dupla `(cohorte, mes)`, inmutabilizando todos los registros de ese período (RN-22, RN-37).

#### Scenario: Cierre exitoso
- **WHEN** FINANZAS solicita `POST /api/liquidaciones/cerrar` con `cohorte_id=<id>` y `periodo=2026-06`
- **THEN** el sistema transiciona todas las liquidaciones `Abierta` de esa dupla a `Cerrada`, registra auditoría `LIQUIDACION_CERRAR`, y retorna 200 con cantidad de liquidaciones cerradas.

#### Scenario: Cierre sin liquidaciones calculadas
- **WHEN** no existen liquidaciones en estado `Abierta` para la dupla indicada
- **THEN** el sistema retorna 404 con mensaje "No hay liquidaciones abiertas para cerrar".

#### Scenario: Cierre sin permiso
- **WHEN** un usuario sin permiso `liquidaciones:cerrar` intenta cerrar
- **THEN** el sistema retorna 403.

### Requirement: Liquidación cerrada es inmutable
El sistema SHALL rechazar cualquier intento de modificar una liquidación en estado `Cerrada`.

#### Scenario: Intento de modificar liquidación cerrada
- **WHEN** se intenta modificar cualquier campo de una `Liquidacion` con `estado=Cerrada`
- **THEN** el sistema retorna 409 con mensaje "Liquidación cerrada no puede modificarse".

#### Scenario: Intento de recalcular liquidación cerrada
- **WHEN** se intenta `POST /api/liquidaciones/{id}/recalcular` sobre una liquidación cerrada
- **THEN** el sistema retorna 409.

### Requirement: Auditoría de cierre
El sistema SHALL registrar en `AuditLog` cada operación de cierre con código `LIQUIDACION_CERRAR`, incluyendo `cohorte_id`, `periodo`, `cantidad` de liquidaciones afectadas y `usuario_id` del operador.

#### Scenario: Registro de auditoría en cierre
- **WHEN** se cierran 15 liquidaciones para `(cohorte_id=X, periodo=2026-06)`
- **THEN** se crea un `AuditLog` con `accion=LIQUIDACION_CERRAR`, `detalle={cohorte_id, periodo, cantidad: 15}`.
