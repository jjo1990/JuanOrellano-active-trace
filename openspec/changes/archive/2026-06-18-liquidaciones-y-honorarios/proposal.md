## Why

El sistema ya gestiona usuarios, asignaciones, estructura académica y el ciclo completo importar→analizar→comunicar, pero no puede calcular ni cerrar las liquidaciones de honorarios docentes. FINANZAS necesita una herramienta para determinar cuánto cobra cada docente por período (Base + Plus), inmutabilizar ese cálculo al cerrarlo, y gestionar por separado a los docentes que facturan como monotributistas. Sin este módulo, la plataforma no cubre el ciclo completo de gestión académica→administrativa.

## What Changes

- **Nuevos modelos**: `SalarioBase` (monto base por rol con vigencia), `SalarioPlus` (adicional por grupo de materias × rol con vigencia), `Liquidacion` (resumen por docente × cohorte × mes, con estado Abierta/Cerrada), `Factura` (comprobante de docentes monotributistas, estado Pendiente/Abonada).
- **Extensión de Materia**: nuevo campo `grupo_plus` (texto, nullable) para mapear cada materia a su grupo de plus (resuelve PA-22).
- **Cálculo de liquidación**: `Total = Base(rol vigente) + Σ(Plus(grupo, rol) × N_comisiones)` por docente, cohorte y mes (RN-21, RN-33, RN-34, PA-23).
- **Cierre inmutable**: liquidación Abierta → Cerrada; una vez cerrada no se modifica (RN-22).
- **Separación contable**: docentes facturantes excluidos del total de liquidación; NEXO visibilizado por separado pero incluido en total (RN-35, RN-36, RN-38).
- **Validación de datos bancarios**: docente sin CBU/alias no se incluye en liquidación procesable (RN-26).
- **ABM de grilla salarial**: FINANZAS gestiona SalarioBase y SalarioPlus con vigencia temporal (RN-31, RN-32).
- **ABM de facturas**: carga, consulta y cambio de estado (Pendiente ↔ Abonada) para docentes facturantes (RN-39, RN-40).
- **Endpoints REST**: `/api/liquidaciones/*` (calcular, ver, cerrar, historial), `/api/salarios/*` (base y plus), `/api/facturas/*` (CRUD + cambio de estado).
- **Auditoría**: registra `LIQUIDACION_CERRAR`, `LIQUIDACION_CALCULAR`, `SALARIO_MODIFICAR`, `FACTURA_CARGAR`, `FACTURA_ABONAR`.
- **Migración**: nuevas tablas + columna `grupo_plus` en `materias`.

## Capabilities

### New Capabilities
- `salario-base`: ABM de la grilla de salario base por rol con vigencia temporal desde/hasta.
- `salario-plus`: ABM de la grilla de plus salarial por grupo de materias × rol con vigencia.
- `liquidacion-calculo`: Cálculo de liquidación mensual Base + Σ(Plus × N_comisiones) por docente × cohorte × mes, con segmentación contable (general / NEXO / facturantes).
- `liquidacion-cierre`: Cierre inmutable de una liquidación (cohorte × mes). Una vez cerrada no admite modificaciones.
- `factura-gestion`: ABM de facturas de docentes monotributistas: alta, consulta con filtros y cambio de estado Pendiente ↔ Abonada.

### Modified Capabilities
- `estructura-academica`: agregar campo `grupo_plus` a Materia (texto, nullable) — requisito para el cálculo de plus (PA-22).

## Impact

- **Modelos nuevos**: `SalarioBase`, `SalarioPlus`, `Liquidacion`, `Factura` en `backend/app/models/`
- **Modelo modificado**: `Materia` (nuevo campo `grupo_plus`)
- **Repositorios nuevos**: `SalarioBaseRepository`, `SalarioPlusRepository`, `LiquidacionRepository`, `FacturaRepository`
- **Servicios nuevos**: `LiquidacionService` (cálculo, cierre, segmentación), `FacturaService`
- **Routers nuevos**: `liquidaciones.py`, `salarios.py`, `facturas.py`
- **Schemas nuevos**: DTOs para request/response de los 3 módulos
- **Migración**: nuevas tablas + ALTER TABLE materias ADD grupo_plus
- **Permisos**: `liquidaciones:calcular`, `liquidaciones:ver`, `liquidaciones:cerrar`, `liquidaciones:configurar-salarios`, `liquidaciones:administrar-grilla`, `facturas:gestionar`
- **Tests**: unitarios de cálculo, integración de API, validación de reglas de negocio (RN-21 a RN-40)
- **Dependencias**: C-07 (usuarios-y-asignaciones) — necesita Asignacion para determinar comisiones del docente
