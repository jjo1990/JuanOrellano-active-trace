## ADDED Requirements

### Requirement: Listado de facturas con filtros
El sistema SHALL mostrar una tabla de comprobantes de docentes que facturan, con filtros por docente, estado (pendiente/abonada), rango de fechas y búsqueda libre.

#### Scenario: Ver facturas pendientes
- **WHEN** el usuario filtra por estado "Pendiente"
- **THEN** el sistema muestra solo las facturas en estado pendiente.

#### Scenario: Buscar factura por docente
- **WHEN** el usuario escribe el nombre de un docente en el campo de búsqueda
- **THEN** el sistema filtra las facturas mostrando solo las del docente buscado.

### Requirement: Cambio de estado de factura
El sistema SHALL permitir cambiar el estado de un comprobante entre Pendiente y Abonada, registrando la fecha del cambio.

#### Scenario: Marcar factura como abonada
- **WHEN** el usuario hace clic en "Marcar como abonada" en una factura pendiente
- **THEN** el sistema cambia el estado a "Abonada", registra la fecha de pago, y actualiza la tabla.

#### Scenario: Revertir factura a pendiente
- **WHEN** el usuario hace clic en "Revertir a pendiente" en una factura abonada
- **THEN** el sistema cambia el estado a "Pendiente" y limpia la fecha de pago.

### Requirement: Detalle de factura
El sistema SHALL mostrar el detalle completo de una factura: fecha de carga, docente, período facturado, detalle, archivo adjunto con nombre y tamaño, estado y datos de pago.

#### Scenario: Ver detalle de factura
- **WHEN** el usuario hace clic en una fila de la tabla de facturas
- **THEN** el sistema expande la fila mostrando el detalle completo del comprobante.
