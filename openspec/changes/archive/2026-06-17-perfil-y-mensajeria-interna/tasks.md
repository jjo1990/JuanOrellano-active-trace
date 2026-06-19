## 1. Perfil — Schemas

- [x] 1.1 Crear `backend/app/schemas/perfil.py` con `PerfilUpdate` (campos editables: nombre, apellidos, dni, banco, cbu, alias_cbu, regional, email, legajo, legajo_profesional, facturador — excluye CUIL, password, activo; `model_config = ConfigDict(extra='forbid')`)
- [x] 1.2 Crear `PerfilResponse` en el mismo archivo (incluye todos los campos: id, tenant_id, nombre, apellidos, email, dni, cuil, cbu, alias_cbu, banco, regional, legajo, legajo_profesional, facturador, activo, created_at, updated_at; `model_config = ConfigDict(extra='forbid', from_attributes=True)`)

## 2. Perfil — Service

- [x] 2.1 Crear `backend/app/services/perfil_service.py` con `PerfilService` que recibe `AsyncSession` y `tenant_id`, usa `UserRepository`, expone `get_perfil(user_id) -> PerfilResponse` y `update_perfil(user_id, data: PerfilUpdate) -> PerfilResponse`
- [x] 2.2 `get_perfil` obtiene el User por ID vía repo, mapea a PerfilResponse (los EncryptedField auto-descifran al leer del modelo)
- [x] 2.3 `update_perfil` obtiene el User, aplica `model_dump(exclude_unset=True)` sobre la entidad, maneja IntegrityError de email duplicado como 409, commitea

## 3. Perfil — Router

- [x] 3.1 Crear `backend/app/api/v1/routers/perfil.py` con `APIRouter(prefix="/api/perfil", tags=["perfil"])`
- [x] 3.2 `GET /api/perfil` — usa `Depends(get_current_user)`, llama a `PerfilService.get_perfil(user.id)`, retorna `PerfilResponse`
- [x] 3.3 `PATCH /api/perfil` — usa `Depends(get_current_user)`, recibe `PerfilUpdate`, llama a `PerfilService.update_perfil(user.id, body)`, retorna `PerfilResponse`
- [x] 3.4 Registrar el router en `backend/app/main.py` (desviación: main.py usa `include_router`, no `__init__.py`)

## 4. Inbox — Modelo Mensaje y Migración

- [x] 4.1 Crear `backend/app/models/mensaje.py` con modelo `Mensaje(BaseModelMixin, Base)`: tabla `mensaje`, columnas `remitente_id` (FK user), `destinatario_id` (FK user), `asunto` (String 255), `cuerpo` (Text), `mensaje_padre_id` (FK mensaje, nullable), `leido` (Boolean, default False). Índices: `(tenant_id, destinatario_id, leido)`, `(tenant_id, mensaje_padre_id)`
- [x] 4.2 Crear migración `019_create_mensaje.py` manualmente (alembic --autogenerate falló porque la DB no tenía todas las migraciones previas aplicadas; la migración manual solo crea la tabla `mensaje`)
- [x] 4.3 Importar `Mensaje` en `backend/app/models/__init__.py`

## 5. Inbox — Repository

- [x] 5.1 Crear `backend/app/repositories/mensaje_repository.py` con `MensajeRepository(Repository[Mensaje])`
- [x] 5.2 Método `list_threads_for_user(user_id) -> Sequence[Mensaje]`: query que devuelve mensajes raíz (`mensaje_padre_id IS NULL`) donde `destinatario_id = user_id`, ordenados por `created_at DESC`
- [x] 5.3 Método `get_thread(mensaje_id) -> tuple[Mensaje, list[Mensaje]]`: obtiene el mensaje raíz + todas las respuestas (`mensaje_padre_id = mensaje_id`) ordenadas por `created_at ASC`
- [x] 5.4 Método `user_can_access_thread(user_id, mensaje_id) -> bool`: verifica que el usuario sea destinatario del mensaje raíz o remitente de alguna respuesta

## 6. Inbox — Schemas

- [x] 6.1 Crear `backend/app/schemas/mensaje.py` con:
  - `MensajeCreate`: destinatario_id (UUID), asunto (str), cuerpo (str) — `model_config = ConfigDict(extra='forbid')`
  - `MensajeReplyCreate`: cuerpo (str) — `model_config = ConfigDict(extra='forbid')`
  - `MensajeResponse`: id, tenant_id, remitente (id, nombre, apellidos), destinatario (id, nombre, apellidos), asunto, cuerpo, mensaje_padre_id, leido, created_at — `model_config = ConfigDict(extra='forbid', from_attributes=True)`
  - `ThreadListItem`: datos resumidos del mensaje raíz + cantidad_respuestas (int) + ultima_respuesta_at (datetime | None)
  - `ThreadDetailResponse`: mensaje raíz (MensajeResponse) + respuestas (list[MensajeResponse])

## 7. Inbox — Service

- [x] 7.1 Crear `backend/app/services/mensaje_service.py` con `MensajeService` que recibe `AsyncSession` y `tenant_id`
- [x] 7.2 Método `list_threads(user_id) -> list[ThreadListItem]`: obtiene hilos del repo, arma los ThreadListItem con metadata de respuestas
- [x] 7.3 Método `get_thread(mensaje_id, user_id) -> ThreadDetailResponse`: verifica acceso vía repo, obtiene hilo, marca mensaje raíz como leído si user es destinatario, commitea
- [x] 7.4 Método `create_message(data: MensajeCreate, remitente_id) -> MensajeResponse`: valida que destinatario exista en el tenant, crea el modelo, persiste, commitea
- [x] 7.5 Método `reply_to_thread(mensaje_id, data: MensajeReplyCreate, remitente_id) -> MensajeResponse`: verifica acceso, obtiene el destinatario de la respuesta (remitente original del mensaje raíz si el que responde es el destinatario, o el destinatario original si responde el remitente), crea mensaje con `mensaje_padre_id`, persiste, commitea

## 8. Inbox — Router

- [x] 8.1 Crear `backend/app/api/v1/routers/inbox.py` con `APIRouter(prefix="/api/inbox", tags=["inbox"])`
- [x] 8.2 `GET /api/inbox` — usa `Depends(get_current_user)`, llama a `MensajeService.list_threads(user.id)`, retorna `list[ThreadListItem]`
- [x] 8.3 `GET /api/inbox/{id}` — usa `Depends(get_current_user)`, llama a `MensajeService.get_thread(id, user.id)`, retorna `ThreadDetailResponse`
- [x] 8.4 `POST /api/inbox` — usa `Depends(get_current_user)`, recibe `MensajeCreate`, llama a `MensajeService.create_message(body, user.id)`, retorna `MensajeResponse` con status 201
- [x] 8.5 `POST /api/inbox/{id}/reply` — usa `Depends(get_current_user)`, recibe `MensajeReplyCreate`, llama a `MensajeService.reply_to_thread(id, body, user.id)`, retorna `MensajeResponse` con status 201
- [x] 8.6 Registrar el router en `backend/app/main.py` (desviación: main.py usa `include_router`, no `__init__.py`)

## 9. Tests — Perfil

- [x] 9.1 Escribir tests en `backend/tests/test_perfil.py`: test_get_perfil_ok, test_get_perfil_sin_auth (401/403), test_update_perfil_ok, test_update_perfil_cuil_rechazado (422), test_update_perfil_email_duplicado (409), test_update_perfil_password_rechazado (422), test_perfil_response_incluye_pii
- [x] 9.2 Verificar que los tests pasan con `pytest backend/tests/test_perfil.py -v`

## 10. Tests — Inbox

- [x] 10.1 Escribir tests en `backend/tests/test_inbox.py`: test_list_threads_vacio, test_list_threads_con_mensajes, test_get_thread_como_destinatario, test_get_thread_como_participante, test_get_thread_sin_permiso (404), test_create_message_ok, test_create_message_destinatario_inexistente (404), test_create_message_sin_asunto (422), test_create_message_sin_cuerpo (422), test_reply_to_thread_ok, test_reply_sin_participante (404), test_tenant_isolation_inbox
- [x] 10.2 Verificar que los tests pasan con `pytest backend/tests/test_inbox.py -v`

## 11. Integración y Verificación

- [x] 11.1 Verificar que el router de perfil y el de inbox están registrados y responden en `GET /api/docs`
- [x] 11.2 Ejecutar linter: ruff check en todos los archivos nuevos — All checks passed
- [x] 11.3 Ejecutar tests: 55 passed (11 perfil + 18 inbox + 2 health + 7 usuarios + 17 tarea_service) — sin regresiones
- [x] 11.4 Verificar cobertura de reglas de negocio: ≥90% en tests de perfil e inbox
