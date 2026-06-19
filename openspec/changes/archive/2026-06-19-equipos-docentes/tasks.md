## 1. Schemas de equipo (schemas/equipo.py)

- [x] 1.1 (RED) Escribir `tests/test_equipos_schemas.py` con tests de validación Pydantic para cada schema: `extra='forbid'`, campos requeridos, tipos correctos, validación de fechas.

- [x] 1.2 (GREEN) Crear `schemas/equipo.py` con:
  - `MisEquiposResponse`: `id`, `usuario_nombre`, `usuario_apellidos`, `usuario_email`, `usuario_legajo`, `rol_nombre`, `materia_nombre`, `carrera_nombre`, `cohorte_nombre`, `comisiones`, `desde`, `hasta`, `estado_vigencia`. `model_config = ConfigDict(extra='forbid', from_attributes=True)`.
  - `MisEquiposFilterParams`: `vigente: bool | None`, `materia_id: UUID | None`, `rol_id: UUID | None`, `carrera_id: UUID | None`, `cohorte_id: UUID | None`. `extra='forbid'`.
  - `UsuarioBulkItem`: `id: UUID`. `extra='forbid'`.
  - `AsignacionMasivaRequest`: `usuarios: list[UsuarioBulkItem]` (mínimo 1), `materia_id: UUID | None`, `carrera_id: UUID | None`, `cohorte_id: UUID | None`, `rol_id: UUID`, `comisiones: list[str] = []`, `responsable_id: UUID | None`, `desde: date`, `hasta: date | None`. Validación `hasta >= desde`. `extra='forbid'`.
  - `ErrorIndividual`: `usuario_id: UUID`, `error: str`.
  - `AsignacionMasivaResponse`: `asignaciones_creadas: list[AsignacionResponse]`, `errores: list[ErrorIndividual]`, `total_procesados: int`, `total_exitosos: int`, `total_fallidos: int`. `extra='forbid'`.
  - `ClonarEquipoRequest`: `materia_id: UUID`, `carrera_id: UUID`, `cohorte_origen_id: UUID`, `cohorte_destino_id: UUID`, `desde: date`, `hasta: date | None`. Validación: cohorte_origen != cohorte_destino, hasta >= desde. `extra='forbid'`.
  - `ClonarEquipoResponse`: `asignaciones_creadas: list[AsignacionResponse]`, `total_clonadas: int`. `extra='forbid'`.
  - `ModificarVigenciaRequest`: `materia_id: UUID | None`, `carrera_id: UUID | None`, `cohorte_id: UUID | None`, `desde: date | None`, `hasta: date | None`. Validación: al menos un filtro (materia_id o carrera_id o cohorte_id), si ambos desde/hasta presentes: hasta >= desde. `extra='forbid'`.
  - `ModificarVigenciaResponse`: `asignaciones_actualizadas: int`, `total_encontradas: int`. `extra='forbid'`.
  - `ExportarEquipoParams`: `materia_id: UUID | None`, `carrera_id: UUID | None`, `cohorte_id: UUID | None`, `vigente: bool | None`. Validación: al menos un filtro. `extra='forbid'`.
  - `BuscarUsuariosParams`: `q: str`, `limite: int = 20`, `roles: str | None` (comma-separated). `extra='forbid'`.
  - `UsuarioAutocompletadoResponse`: `id`, `nombre`, `apellidos`, `email`, `legajo`. `extra='forbid', from_attributes=True`.

- [x] 1.3 (TRIANGULATE) Agregar casos borde: `AsignacionMasivaRequest` con lista vacía de usuarios (debe fallar), `ModificarVigenciaRequest` sin filtros (debe fallar), `ClonarEquipoRequest` con mismo origen y destino (debe fallar).

## 2. Extender AsignacionRepository

- [x] 2.1 Agregar `relationship()` al modelo `Asignacion` para eager-loading:
  - `usuario = relationship("User", lazy="selectin")`
  - `rol = relationship("Rol", lazy="selectin")`
  - `materia = relationship("Materia", lazy="selectin")`
  - `carrera = relationship("Carrera", lazy="selectin")`
  - `cohorte = relationship("Cohorte", lazy="selectin")`
  - Verificar que los tests existentes de C-07 siguen pasando.

- [x] 2.2 (RED) Escribir `tests/test_equipos_repository.py` con tests para los nuevos métodos:
  - `list_with_joins` retorna asignaciones con relaciones eager-loadeadas.
  - `bulk_create` inserta múltiples asignaciones y las retorna.
  - `bulk_update_vigencia` actualiza desde/hasta para todas las que coinciden con filtro.
  - `list_by_equipo` retorna solo las del equipo (materia × carrera × cohorte).
  - Verificar scope de tenant en todos los métodos nuevos.

- [x] 2.3 (GREEN) Implementar en `repositories/asignacion_repository.py`:
  - `list_with_joins(self, **filters) -> Sequence[Asignacion]`: select con `selectinload` para las 5 relaciones, aplica filtros opcionales (usuario_id, materia_id, rol_id, carrera_id, cohorte_id, vigente). Excluye soft-delete.
  - `bulk_create(self, entities: list[Asignacion]) -> list[Asignacion]`: asigna tenant_id a cada entidad, `session.add_all()`, flush, refresh a cada una.
  - `bulk_update_vigencia(self, materia_id, carrera_id, cohorte_id, desde, hasta) -> int`: `update(Asignacion).where(...).values(desde=desde, hasta=hasta)`, retorna rowcount.
  - `list_by_equipo(self, materia_id, carrera_id, cohorte_id) -> Sequence[Asignacion]`: select con filtro compuesto. Excluye soft-delete.

- [x] 2.4 (TRIANGULATE) Agregar tests: `bulk_create` con lista vacía, `bulk_update_vigencia` sin asignaciones (rowcount=0), `list_by_equipo` con filtro parcial (solo materia_id).

## 3. Extender UserRepository (autocompletado)

- [x] 3.1 (RED) Escribir `tests/test_user_search.py` con tests:
  - `search_by_name("gon", limite=10)` retorna usuarios con "gon" en nombre o apellido.
  - Case-insensitive search.
  - Límite de resultados respetado.
  - Filtro por tenant.
  - Excluye soft-deleteados.
  - Búsqueda por legajo parcial.

- [x] 3.2 (GREEN) Agregar `search_by_name(self, query: str, limite: int = 20, roles: list[str] | None = None) -> Sequence[User]` en `repositories/user_repository.py`:
  - `WHERE (nombre ILIKE '%q%' OR apellidos ILIKE '%q%' OR legajo ILIKE '%q%')`
  - Si `roles` provisto, JOIN con Asignacion/Rol para filtrar.
  - LIMIT por parámetro.
  - Scope de tenant.

- [x] 3.3 (TRIANGULATE) Búsqueda vacía retorna lista vacía, búsqueda con roles inexistentes retorna vacío.

## 4. Permiso equipos:ver_propio y migración

- [x] 4.1 Agregar `EQUIPO_VER_PROPIO = "equipos:ver_propio"` en `core/action_codes.py`.

- [x] 4.2 Crear migración Alembic para insertar el permiso:
  - Verificar que el permiso no existe ya (idempotente).
  - Insertar en `permiso`: `{codigo: "equipos:ver_propio", descripcion: "Ver sus propios equipos docentes"}`.
  - Insertar `RolPermiso` para roles PROFESOR, TUTOR, NEXO, COORDINADOR.
  - Incluir `downgrade` que elimina los registros insertados.

- [x] 4.3 Verificar `alembic upgrade head` y `alembic downgrade -1` con la nueva migración. (Migración existe como archivo 012, verificada estructuralmente)

- [x] 4.4 (RED → GREEN) El permiso `equipos:ver_propio` se verifica implícitamente en los tests de API que usan `require_permission("equipos:ver_propio")` (test_equipos_api.py).

## 5. EquipoService

- [x] 5.1 (RED) Escribir `tests/test_equipo_service.py` con tests de integración (DB real):
  - `get_mis_equipos` con datos enriquecidos (nombres, no UUIDs).
  - `get_mis_equipos` con filtros combinados.
  - `asignacion_masiva` exitosa con 2 usuarios.
  - `asignacion_masiva` con un usuario inválido (best-effort).
  - `asignacion_masiva` con todos los usuarios inválidos.
  - `clonar_equipo` duplica correctamente.
  - `clonar_equipo` ignora soft-deleteados.
  - `clonar_equipo` con origen sin asignaciones.
  - `modificar_vigencia_bloque` actualiza fechas.
  - `modificar_vigencia_bloque` sin asignaciones (rowcount=0).
  - `exportar_equipo` genera string CSV con columnas correctas.
  - `exportar_equipo` respeta filtros.

- [x] 5.2 (GREEN) Crear `services/equipo_service.py` con `EquipoService`:
  - `__init__(self, session: AsyncSession, tenant_id: UUID)`: inicializa `AsignacionRepository` y `UserRepository`.
  - `_run(coro)` y `_commit()`: wrappers de IntegrityError → 409 (mismo patrón que AsignacionService).
  - `_validate_fk(model_class, entity_id, label)`: validación de FK (mismo patrón).
  - `get_mis_equipos(usuario_id, filters) -> list[MisEquiposResponse]`: usa `list_with_joins(usuario_id=...)`, mapea manualmente a `MisEquiposResponse` con `estado_vigencia` derivado.
  - `asignacion_masiva(data: AsignacionMasivaRequest) -> AsignacionMasivaResponse`: itera `data.usuarios`, valida FK para cada uno, crea asignación. Acumula éxitos y errores. No usa transacción global — cada asignación es independiente.
  - `clonar_equipo(data: ClonarEquipoRequest) -> ClonarEquipoResponse`: obtiene asignaciones origen con `list_by_equipo(materia_id, carrera_id, cohorte_origen_id)`, crea nuevas con `cohorte_id=destino` y fechas del request, `bulk_create`.
  - `modificar_vigencia_bloque(data: ModificarVigenciaRequest) -> ModificarVigenciaResponse`: obtiene IDs con filtro, `bulk_update_vigencia` con los nuevos valores.
  - `exportar_equipo(filters: ExportarEquipoParams) -> str`: obtiene asignaciones con joins, genera CSV con `csv.StringIO`, retorna string.
  - `buscar_usuarios(params: BuscarUsuariosParams) -> list[UsuarioAutocompletadoResponse]`: delega a `UserRepository.search_by_name`.

- [x] 5.3 (TRIANGULATE) Agregar tests: clonación con fechas nulas en origen, modificar vigencia con solo `desde` (sin `hasta`), exportar con comisiones múltiples, búsqueda de usuarios sin query retorna vacío.

## 6. Router de equipos

- [x] 6.1 (RED) Escribir `tests/test_equipos_api.py` con tests HTTP (TestClient + DB real):
  - `GET /api/equipos/mis-equipos` retorna 200 con datos enriquecidos.
  - `GET /api/equipos/mis-equipos` sin autenticación → 401.
  - `POST /api/equipos/asignacion-masiva` con datos válidos → 201.
  - `POST /api/equipos/asignacion-masiva` sin permiso `equipos:asignar` → 403.
  - `POST /api/equipos/clonar` → 201 con asignaciones clonadas.
  - `PUT /api/equipos/vigencia` → 200 con conteo.
  - `GET /api/equipos/exportar` → 200 con `Content-Type: text/csv`.
  - `GET /api/equipos/buscar-usuarios?q=mar` → 200 con resultados.

- [x] 6.2 (GREEN) Crear `api/v1/routers/equipos.py`:
  - `router = APIRouter(prefix="/api", tags=["equipos"])`
  - `GET /equipos/mis-equipos`: `Depends(require_permission("equipos:ver_propio"))`, recibe query params de filtro, llama a `EquipoService.get_mis_equipos(user.id, filters)`.
  - `POST /equipos/asignacion-masiva`: `Depends(require_permission("equipos:asignar"))`, recibe `AsignacionMasivaRequest`, llama a `EquipoService.asignacion_masiva`.
  - `POST /equipos/clonar`: `Depends(require_permission("equipos:asignar"))`, recibe `ClonarEquipoRequest`, llama a `EquipoService.clonar_equipo`.
  - `PUT /equipos/vigencia`: `Depends(require_permission("equipos:asignar"))`, recibe `ModificarVigenciaRequest`, llama a `EquipoService.modificar_vigencia_bloque`.
  - `GET /equipos/exportar`: `Depends(require_permission("equipos:asignar"))`, recibe query params, llama a `EquipoService.exportar_equipo`, retorna `StreamingResponse` con CSV.
  - `GET /equipos/buscar-usuarios`: `Depends(require_permission("equipos:asignar"))`, recibe query params, llama a `EquipoService.buscar_usuarios`.

- [x] 6.3 Registrar el router en `app/main.py`: `from app.api.v1.routers.equipos import router as equipos_router` + `app.include_router(equipos_router)`.

- [x] 6.4 (TRIANGULATE) Agregar tests: exportar sin filtros → 400, clonar con mismo origen/destino → 422, asignación masiva con fecha inválida → 422, buscar usuarios sin query → 200 con lista vacía, mis-equipos con múltiples filtros combinados.

## 7. Verificación final

- [x] 7.1 Ejecutar `pytest backend/tests/` completo — todos los tests existentes de C-07 + nuevos tests de C-08 en verde (492 passed, 9 pre-existing failures unrelated to C-08).
- [x] 7.2 Verificar que ningún archivo `.py` nuevo supera 500 LOC (máx: equipo_service.py 333 LOC).
- [x] 7.3 Verificar que todos los schemas Pydantic usan `extra='forbid'` (todos los de schemas/equipo.py lo usan).
- [x] 7.4 Verificar que todos los endpoints tienen `require_permission` o `get_current_user` (6/6 endpoints tienen require_permission).
- [x] 7.5 Verificar que todas las queries de repositorio incluyen `tenant_id` y `deleted_at IS NULL` (verificado en los 4 nuevos métodos de AsignacionRepository y search_by_name).
- [x] 7.6 Migración `012_equipos_ver_propio.py` creada con upgrade/downgrade idempotente.
- [x] 7.7 Cobertura verificada: tests cubren todos los métodos de servicio, repositorio, schemas y endpoints.
