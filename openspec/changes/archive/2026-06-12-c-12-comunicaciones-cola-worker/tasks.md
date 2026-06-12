## 1. Migracion y Modelo

- [x] 1.1 Crear migracion Alembic 011: tabla `comunicacion` con columnas, FKs, check constraint en `estado`, e indices (`ix_comunicacion_estado`, `ix_comunicacion_lote`, `ix_comunicacion_materia`)
- [x] 1.2 Ejecutar migracion contra DB de test y verificar que la tabla se crea correctamente
- [x] 1.3 Crear `backend/app/models/comunicacion.py` con clase `Comunicacion(BaseModelMixin, Base)` incluyendo `destinatario_encrypted` + descriptor `destinatario = EncryptedField()`, y columna `estado` con validacion de enum
- [x] 1.4 Agregar import de `Comunicacion` en `backend/app/models/__init__.py`
- [x] 1.5 Verificar que `destinatario` se cifra/descifra correctamente usando `EncryptedField` (test de integracion con DB)

## 2. Maquina de Estados (validate_transition)

- [x] 2.1 Crear `backend/app/services/comunicacion_service.py` con funcion pura `validate_transition(estado_actual: str, estado_nuevo: str) -> bool` que implementa RN-15
- [x] 2.2 Test unitario: todas las transiciones validas retornan True (Pendiente→Enviando, Enviando→Enviado, Enviando→Error, Pendiente→Cancelado)
- [x] 2.3 Test unitario: cada transicion invalida lanza ValueError con mensaje descriptivo
- [x] 2.4 Test unitario: transiciones desde estados terminales (Enviado, Error, Cancelado) son siempre invalidas
- [x] 2.5 Test unitario: transicion al mismo estado es invalida

## 3. Template Rendering

- [x] 3.1 Implementar `render_template(template: str, context: dict) -> str` en `comunicacion_service.py` usando `str.replace()` con soporte para `{{nombre}}`, `{{materia}}`, `{{actividades_pendientes}}`, `{{nota_promedio}}`, `{{link_materia}}`
- [x] 3.2 Test: renderizado basico con variables presentes en contexto
- [x] 3.3 Test: variables no definidas en contexto se preservan como texto literal `{{variable}}`
- [x] 3.4 Test: multiples ocurrencias de la misma variable se reemplazan todas
- [x] 3.5 Test: template sin variables se devuelve sin cambios

## 4. Repository

- [x] 4.1 Crear `backend/app/repositories/comunicacion_repository.py` con clase `ComunicacionRepository(Repository[Comunicacion])`
- [x] 4.2 Implementar `get_pendientes(limit: int) -> list[Comunicacion]` que retorna Pendientes ordenadas por `created_at` (excluyendo lotes no aprobados si aplica flag)
- [x] 4.3 Implementar `get_by_lote(lote_id: UUID) -> list[Comunicacion]` con scope tenant
- [x] 4.4 Implementar `get_by_materia(materia_id: UUID, estado: str | None) -> list[Comunicacion]` con scope tenant
- [x] 4.5 Implementar `aprobar_lote(lote_id: UUID) -> int` que actualiza todas las Pendiente del lote (si usamos flag `aprobado`)
- [x] 4.6 Implementar `cancelar_lote(lote_id: UUID) -> int` que transiciona Pendiente→Cancelado para todo el lote
- [x] 4.7 Test de integracion: `get_pendientes` respeta tenant isolation

## 5. Schemas Pydantic

- [x] 5.1 Crear `backend/app/schemas/comunicacion.py` con `extra='forbid'` en todos los schemas
- [x] 5.2 `ComunicacionDTO`: id, enviado_por, materia_id, destinatario (descifrado), asunto, cuerpo, estado, lote_id, enviado_at, created_at
- [x] 5.3 `PreviewRequest`: template (str), alumno_ids (list[UUID]), materia_id (UUID)
- [x] 5.4 `PreviewResponse`: previews (list[{alumno_id, nombre, asunto, cuerpo}])
- [x] 5.5 `EnviarRequest`: template (str), alumno_ids (list[UUID]), materia_id (UUID), asunto (str)
- [x] 5.6 `EnviarResponse`: lote_id (UUID), count (int), estado (str)
- [x] 5.7 `LoteStatusResponse`: lote_id, comunicaciones (list[ComunicacionDTO]), resumen (pendientes, enviados, errores, cancelados)
- [x] 5.8 `CancelarRequest`: motivo (str opcional) — para auditoria

## 6. Service Layer

- [x] 6.1 Implementar `ComunicacionService.__init__(session, tenant_id)` con instanciacion de `ComunicacionRepository`
- [x] 6.2 Implementar `preview(request: PreviewRequest) -> PreviewResponse`: para cada alumno, obtiene datos reales (nombre desde EntradaPadron, nota desde Calificacion), renderiza template con `render_template()`, devuelve previews sin persistir
- [x] 6.3 Implementar `enviar(request: EnviarRequest, user_id: UUID) -> EnviarResponse`: genera `lote_id`, crea una `Comunicacion` por alumno con `render_template()`, persiste con estado `Pendiente`, registra auditoria `COMUNICACION_ENVIAR`
- [x] 6.4 Implementar `aprobar_lote(lote_id: UUID, user_id: UUID) -> LoteStatusResponse`: valida permiso, ejecuta `aprobar_lote` en repo, audita
- [x] 6.5 Implementar `cancelar_lote(lote_id: UUID, motivo: str | None, user_id: UUID) -> LoteStatusResponse`: ejecuta `cancelar_lote` en repo, audita
- [x] 6.6 Implementar `cancelar_individual(id: UUID, user_id: UUID, motivo: str | None) -> ComunicacionDTO`: valida que sea Pendiente, transiciona a Cancelado, audita
- [x] 6.7 Implementar `get_lote_status(lote_id: UUID) -> LoteStatusResponse`
- [x] 6.8 Implementar `get_by_materia(materia_id: UUID, estado: str | None) -> list[ComunicacionDTO]`
- [x] 6.9 Usar `validate_transition()` en todos los cambios de estado del service

## 7. Tests de Service (Strict TDD)

- [x] 7.1 Test: `preview` renderiza correctamente para 1 alumno con datos reales de DB
- [x] 7.2 Test: `preview` no persiste ningun registro en `comunicacion`
- [x] 7.3 Test: `preview` con alumno sin datos devuelve variables sin reemplazar (graceful degradation)
- [x] 7.4 Test: `enviar` crea N comunicaciones con mismo `lote_id` y estado Pendiente
- [x] 7.5 Test: `enviar` renderiza template con datos de cada alumno individualmente
- [x] 7.6 Test: `enviar` registra auditoria `COMUNICACION_ENVIAR`
- [x] 7.7 Test: `aprobar_lote` transiciona todas las Pendiente del lote
- [x] 7.8 Test: `cancelar_lote` transiciona todas las Pendiente del lote a Cancelado
- [x] 7.9 Test: `cancelar_individual` transiciona solo esa comunicacion
- [x] 7.10 Test: `cancelar_individual` falla si la comunicacion no esta en Pendiente
- [x] 7.11 Test: `get_lote_status` devuelve resumen correcto (counts por estado)
- [x] 7.12 Test: `get_by_materia` filtra correctamente y respeta tenant
- [x] 7.13 Test: `destinatario` se almacena cifrado y se lee descifrado

## 8. Router

- [x] 8.1 Crear `backend/app/api/v1/routers/comunicaciones.py` con `APIRouter(prefix="/api/comunicaciones", tags=["comunicaciones"])`
- [x] 8.2 `POST /preview` con guard `require_permission("comunicacion:enviar")`, recibe `PreviewRequest`, delega a `ComunicacionService.preview()`
- [x] 8.3 `POST /enviar` con guard `require_permission("comunicacion:enviar")`, recibe `EnviarRequest`, delega a `ComunicacionService.enviar()`
- [x] 8.4 `GET /lote/{lote_id}` con guard `require_permission("comunicacion:enviar")`, delega a `ComunicacionService.get_lote_status()`
- [x] 8.5 `GET /materia/{materia_id}` con guard `require_permission("comunicacion:enviar")`, query param `?estado=`, delega a `ComunicacionService.get_by_materia()`
- [x] 8.6 `POST /aprobar/{lote_id}` con guard `require_permission("comunicacion:aprobar")`, delega a `ComunicacionService.aprobar_lote()`
- [x] 8.7 `POST /cancelar/{id}` con guard `require_permission("comunicacion:enviar")`, delega a `ComunicacionService.cancelar_individual()`
- [x] 8.8 Registrar router en `backend/app/api/v1/routers/__init__.py` (agregar `comunicaciones.router`)
- [x] 8.9 Test de integracion: `POST /api/comunicaciones/preview` retorna 200 con datos correctos
- [x] 8.10 Test de integracion: `POST /api/comunicaciones/enviar` sin permiso retorna 403
- [x] 8.11 Test de integracion: `POST /api/comunicaciones/aprobar/{lote_id}` sin permiso `comunicacion:aprobar` retorna 403
- [x] 8.12 Test de integracion: flujo completo preview → enviar → aprobar → consultar lote

## 9. Worker

- [x] 9.1 Crear `backend/app/workers/dispatch_worker.py` con `_send_email(destinatario, asunto, cuerpo) -> bool` mockeada: loguea y retorna True
- [x] 9.2 Implementar `run_worker(session_factory, poll_interval=5, batch_size=10)` como `async` loop
- [x] 9.3 Worker consulta `ComunicacionRepository.get_pendientes(limit=batch_size)`
- [x] 9.4 Worker transiciona cada Pendiente → Enviando → `_send_email()` → Enviado/Error con `validate_transition()`
- [x] 9.5 Worker establece `enviado_at` al completar exitosamente
- [x] 9.6 Worker maneja excepciones: captura, loguea, marca Error, continua con siguiente
- [x] 9.7 Agregar entry point `if __name__ == "__main__": asyncio.run(run_worker(...))`
- [x] 9.8 Test: worker procesa comunicacion Pendiente → Enviado (mock `_send_email` retorna True)
- [x] 9.9 Test: worker marca Error cuando `_send_email` lanza excepcion
- [x] 9.10 Test: worker respeta `batch_size` (solo procesa N por iteracion)
- [x] 9.11 Test: worker no procesa comunicaciones de lote no aprobado (si aplica flag de aprobacion)

## 10. Integracion y Verificacion

- [x] 10.1 Ejecutar migracion completa y verificar schema en DB real/post-test
- [x] 10.2 Verificar que todos los endpoints aparecen en OpenAPI docs (`/docs`)
- [x] 10.3 Verificar tenant isolation: dos tenants no ven las comunicaciones del otro
- [x] 10.4 Verificar soft-delete: `GET /lote/{lote_id}` no incluye comunicaciones con `deleted_at IS NOT NULL`
- [x] 10.5 Ejecutar suite completa de tests (`pytest tests/test_comunicacion_* -v`) y verificar coverage ≥80%
- [x] 10.6 Ejecutar linter/formatter sobre todos los archivos nuevos
- [x] 10.7 Revisar que no haya imports circulares ni warnings
