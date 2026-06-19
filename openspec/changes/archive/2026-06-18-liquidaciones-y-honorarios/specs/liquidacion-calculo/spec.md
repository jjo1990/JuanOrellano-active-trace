## ADDED Requirements

### Requirement: Calcular liquidación del período
El sistema SHALL calcular, para cada docente con asignaciones vigentes en la cohorte y mes indicados, su liquidación según la fórmula `Total = Base(rol) + Σ(Plus(grupo, rol) × N_comisiones)` (RN-34) y persistir los resultados en estado `Abierta`.

#### Scenario: Cálculo exitoso con un docente
- **WHEN** FINANZAS solicita `POST /api/liquidaciones/calcular` con `cohorte_id=<id>` y `periodo=2026-06`
- **THEN** el sistema calcula y persiste una `Liquidacion` por cada docente con asignaciones vigentes, retorna 201 con array de liquidaciones creadas (incluyendo desglose base/plus/total).

#### Scenario: Docente sin datos bancarios se omite con advertencia
- **WHEN** un docente con asignaciones vigentes no tiene `cbu` ni `alias_cbu` registrados
- **THEN** el sistema omite a ese docente del cálculo e incluye una advertencia en la respuesta con `usuario_id` y motivo.

#### Scenario: Docente facturante se incluye pero marcado como excluido
- **WHEN** un docente tiene `modalidad_pago=facturante`, se calcula su liquidación pero con `excluido_por_factura=true`
- **THEN** el total general de la respuesta no incluye su monto, y el docente aparece en el segmento "facturantes".

#### Scenario: Cohorte sin asignaciones vigentes
- **WHEN** la cohorte no tiene docentes con asignaciones vigentes en el período
- **THEN** el sistema retorna 200 con array vacío y mensaje informativo.

### Requirement: Docente con múltiples roles toma la base del rol de mayor jerarquía
El sistema SHALL determinar el `monto_base` de un docente tomando el `SalarioBase` vigente de mayor monto entre los roles de sus asignaciones activas.

#### Scenario: Docente con roles PROFESOR y TUTOR
- **WHEN** un docente tiene asignaciones como PROFESOR (base $80,000) y como TUTOR (base $50,000)
- **THEN** su liquidación usa `monto_base=$80,000` (el mayor).

### Requirement: Plus se acumula por comisión
El sistema SHALL acumular el `SalarioPlus` multiplicado por la cantidad de comisiones del docente en cada grupo de materias (RN-33).

#### Scenario: Tres comisiones del mismo grupo
- **WHEN** un PROFESOR tiene 3 asignaciones en materias con `grupo_plus=PROG` y `SalarioPlus(PROG, PROFESOR)=$15,000`
- **THEN** su `monto_plus` incluye `$15,000 × 3 = $45,000` para ese grupo.

#### Scenario: Comisiones de distintos grupos
- **WHEN** un docente tiene 2 comisiones PROG y 1 comisión BD, con plus PROG=$15,000 y BD=$10,000
- **THEN** su `monto_plus = $15,000×2 + $10,000×1 = $40,000`.

#### Scenario: Materia sin grupo_plus no genera plus
- **WHEN** una asignación es en una materia con `grupo_plus=null`
- **THEN** esa comisión no contribuye al cálculo de plus.

### Requirement: Vista de liquidación con segmentación contable
El sistema SHALL exponer la vista de liquidación segmentada en tres grupos: general (PROFESOR/TUTOR/COORDINADOR no facturantes), NEXO (visible por separado, incluido en total), y facturantes (visibles pero excluidos del total) según F10.6, RN-36, RN-38.

#### Scenario: Vista segmentada
- **WHEN** se solicita `GET /api/liquidaciones?cohorte_id=<id>&periodo=2026-06`
- **THEN** el sistema retorna 200 con objeto que contiene `general` (array), `nexo` (array), `facturantes` (array), `total_sin_factura` (decimal) y `total_con_factura` (decimal).

### Requirement: Recalcular liquidación abierta
El sistema SHALL permitir recalcular una liquidación en estado `Abierta`, actualizando sus montos según la grilla salarial vigente al momento del recálculo.

#### Scenario: Recalcular liquidación abierta
- **WHEN** FINANZAS solicita `POST /api/liquidaciones/{id}/recalcular`
- **THEN** el sistema recalcula base y plus con los valores vigentes, actualiza los montos, y retorna 200.

#### Scenario: No se puede recalcular liquidación cerrada
- **WHEN** se intenta recalcular una liquidación en estado `Cerrada`
- **THEN** el sistema retorna 409.

### Requirement: Historial de liquidaciones
El sistema SHALL permitir consultar liquidaciones de períodos anteriores con filtros por cohorte, período y docente.

#### Scenario: Consulta de historial
- **WHEN** FINANZAS solicita `GET /api/liquidaciones/historial?cohorte_id=<id>&periodo=2026-03`
- **THEN** el sistema retorna 200 con las liquidaciones cerradas de ese período.
