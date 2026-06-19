## ADDED Requirements

### Requirement: Vista de liquidaciones del período con segmentación
El sistema SHALL mostrar la liquidación del período seleccionado segmentada en tres vistas: General (PROFESOR, TUTOR, COORDINADOR que no facturan), NEXO (calculado por separado), y Docentes que facturan (excluidos del total). Cada segmento SHALL mostrar una tabla con columnas: docente, rol, materias a cargo, salario base, plus aplicables y total.

#### Scenario: Ver segmento General con KPIs
- **WHEN** el usuario accede a la vista de liquidaciones y selecciona un período (cohorte + mes)
- **THEN** el sistema muestra 3 tabs (General, NEXO, Factura), KPIs de cabecera "Total sin factura" y "Total con factura", y la tabla del segmento activo.

#### Scenario: Cambiar entre segmentos
- **WHEN** el usuario hace clic en el tab "NEXO"
- **THEN** el sistema muestra la tabla filtrada solo con docentes de rol NEXO, y los KPIs de cabecera permanecen visibles.

#### Scenario: Filtrar por docente
- **WHEN** el usuario escribe un nombre de docente en el campo de búsqueda
- **THEN** el sistema filtra la tabla activa mostrando solo las filas que coinciden con el docente buscado.

### Requirement: Cerrar liquidación del período
El sistema SHALL permitir al usuario FINANZAS cerrar la liquidación del período activo, inmutabilizándola. La acción es irreversible y requiere confirmación explícita.

#### Scenario: Cerrar liquidación con confirmación
- **WHEN** el usuario con permiso `liquidaciones:cerrar` presiona "Cerrar liquidación"
- **THEN** el sistema muestra un modal de confirmación con advertencia de irreversibilidad.
- **WHEN** el usuario confirma el cierre
- **THEN** el sistema cierra la liquidación y recarga la vista mostrando el estado cerrado.

#### Scenario: Usuario sin permiso no ve botón de cierre
- **WHEN** un usuario sin permiso `liquidaciones:cerrar` accede a la vista
- **THEN** el botón "Cerrar liquidación" no está visible.

### Requirement: Detalle individual por docente
El sistema SHALL permitir expandir una fila de docente para ver el detalle del cálculo (materias, comisiones, plus aplicados con su clave y monto).

#### Scenario: Expandir detalle de docente
- **WHEN** el usuario hace clic en una fila de docente en la tabla de liquidación
- **THEN** el sistema expande la fila mostrando el desglose de materias, comisiones, salario base y cada plus con su clave y monto individual.
