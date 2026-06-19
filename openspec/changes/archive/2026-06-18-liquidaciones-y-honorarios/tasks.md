## 1. Modelos y Migración

- [x] 1.1 Agregar `grupo_plus` (VARCHAR, nullable) al modelo `Materia`
- [x] 1.2 Crear modelo `SalarioBase` (id, tenant_id, rol, monto, desde, hasta, soft delete)
- [x] 1.3 Crear modelo `SalarioPlus` (id, tenant_id, grupo, rol, descripcion, monto, desde, hasta, soft delete)
- [x] 1.4 Crear modelo `Liquidacion` (id, tenant_id, cohorte_id, periodo, usuario_id, rol, comisiones, monto_base, monto_plus, total, es_nexo, excluido_por_factura, estado, soft delete)
- [x] 1.5 Crear modelo `Factura` (id, tenant_id, usuario_id, periodo, detalle, referencia_archivo, tamano_kb, estado, cargada_at, abonada_at, soft delete)
- [x] 1.6 Registrar modelos en `backend/app/models/__init__.py`
- [x] 1.7 Crear migración Alembic: tablas nuevas + ALTER TABLE materias ADD grupo_plus

## 2. Repositorios

- [x] 2.1 Crear `SalarioBaseRepository` con scope tenant, filtro por rol y fecha de vigencia
- [x] 2.2 Crear `SalarioPlusRepository` con scope tenant, filtro por grupo, rol y fecha de vigencia
- [x] 2.3 Crear `LiquidacionRepository` con scope tenant, filtro por cohorte+periodo, docente, estado
- [x] 2.4 Crear `FacturaRepository` con scope tenant, filtro por docente, estado, periodo
- [x] 2.5 Extender `MateriaRepository` con filtro por `grupo_plus`

## 3. Schemas Pydantic

- [x] 3.1 Crear `backend/app/schemas/salario.py` — SalarioBaseCreate/Update/Response, SalarioPlusCreate/Update/Response, con validación de solapamiento
- [x] 3.2 Crear `backend/app/schemas/liquidacion.py` — LiquidacionCalcularRequest, LiquidacionResponse, LiquidacionSegmentadaResponse, LiquidacionCerrarRequest
- [x] 3.3 Crear `backend/app/schemas/factura.py` — FacturaCreate/Update/Response, FacturaCambioEstado
- [x] 3.4 Extender `backend/app/schemas/materia.py` — agregar `grupo_plus` opcional a MateriaUpdate y MateriaResponse

## 4. Services

- [x] 4.1 Crear `LiquidacionService` con método `calcular(cohorte_id, periodo)` — lógica Base(rol mayor) + Σ(Plus × N_comisiones), segmentación general/NEXO/facturantes, omisión por datos bancarios
- [x] 4.2 Agregar método `recalcular(liquidacion_id)` — solo si Abierta
- [x] 4.3 Agregar método `cerrar(cohorte_id, periodo)` — transiciona Abierta→Cerrada, registra auditoría
- [x] 4.4 Agregar método `historial(cohorte_id, periodo, filtros)` — consulta de liquidaciones cerradas
- [x] 4.5 Crear `FacturaService` con CRUD + cambio de estado (pendiente ↔ abonada) + validación de docente facturante

## 5. Routers y Endpoints

- [x] 5.1 Crear `backend/app/api/v1/routers/salarios.py` — CRUD `/api/salarios/base` y `/api/salarios/plus`, endpoint de consulta vigente
- [x] 5.2 Crear `backend/app/api/v1/routers/liquidaciones.py` — POST calcular, GET listar segmentado, GET detalle, POST recalcular, POST cerrar, GET historial
- [x] 5.3 Crear `backend/app/api/v1/routers/facturas.py` — CRUD `/api/facturas`, POST abonar/{id}, POST marcar-pendiente/{id}
- [x] 5.4 Registrar routers en `backend/app/main.py`

## 6. Permisos y Seed

- [x] 6.1 Agregar permisos al catálogo: `liquidaciones:calcular`, `liquidaciones:ver`, `liquidaciones:cerrar`, `liquidaciones:configurar-salarios`, `liquidaciones:administrar-grilla`, `facturas:gestionar`
- [x] 6.2 Asignar permisos de liquidación y facturas al rol FINANZAS (y ADMIN lectura)
- [x] 6.3 Declarar guards `require_permission` en cada endpoint según aplique

## 7. Tests

- [x] 7.1 Tests unitarios de `SalarioBaseRepository`: CRUD, filtro por rol, vigencia
- [x] 7.2 Tests unitarios de `SalarioPlusRepository`: CRUD, filtro por grupo/rol, vigencia
- [x] 7.3 Tests unitarios de `LiquidacionRepository`: CRUD, filtro cohorte+periodo, estado
- [x] 7.4 Tests unitarios de `FacturaRepository`: CRUD, filtros
- [x] 7.5 Tests de `LiquidacionService.calcular`: docente único, múltiples roles, acumulación de plus, omisión sin CBU, docente facturante
- [x] 7.6 Tests de `LiquidacionService.cerrar`: cierre exitoso, rechazo sin abiertas, inmutabilidad post-cierre
- [x] 7.7 Tests de `FacturaService`: cambio de estado Pendiente↔Abonada, validación docente facturante
- [x] 7.8 Tests de integración API: endpoints de salarios, liquidaciones, facturas
- [x] 7.9 Tests de seguridad: sin permiso → 403, aislamiento multi-tenant (un tenant no ve liquidaciones de otro)
