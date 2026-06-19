## Context

C-20 implementa las capacidades de la Épica 11 (Perfil y Sesión) y F3.4 (Mensajería interna) del catálogo de funcionalidades. Opera sobre la infraestructura existente de C-01 a C-07: multi-tenancy con row-level isolation, RBAC fino vía `require_permission`, identidad desde JWT, PII cifrada con AES-256 vía `EncryptedField`, soft delete universal y auditoría append-only.

El stack relevante es Python 3.13 + FastAPI + SQLAlchemy 2.0 async + Pydantic v2 (`extra='forbid'`) + Alembic. La arquitectura sigue el flujo unidireccional Routers → Services → Repositories → Models.

## Goals / Non-Goals

**Goals:**
- Permitir que cualquier usuario autenticado edite su perfil (sin intervención del ADMIN)
- Proveer una bandeja de mensajería interna con hilos entre usuarios registrados del sistema
- Reutilizar el endpoint de logout de C-03 sin duplicación de lógica

**Non-Goals:**
- No se modifica el logout de C-03 (ya implementado)
- No se toca el sistema de comunicaciones a alumnos de C-12 (corre paralelo)
- No se implementan notificaciones push/email para nuevos mensajes del inbox
- No se implementa búsqueda full-text en mensajes
- No se implementa "marcar como leído" masivo (solo lectura individual)

## Decisions

### D1: Perfil usa PATCH sobre recurso singular (no PUT con ID)

**Decisión**: `PATCH /api/perfil` — el endpoint opera sobre el usuario de la sesión, no recibe `user_id` por URL. Esto cumple la regla dura #8: identidad SIEMPRE desde la sesión.

**Alternativa descartada**: `PUT /api/perfil/{user_id}` requeriría verificar que `user_id == current_user.id`, lo cual es redundante y va contra el principio de que la identidad sale del JWT.

### D2: Schema PerfilUpdate excluye CUIL y password

**Decisión**: El schema de edición de perfil (`PerfilUpdate`) es un subset del `UsuarioUpdate` existente que excluye:
- `cuil`: es solo lectura (F11.1 lo especifica como no modificable)
- `password`: el cambio de contraseña es un flujo separado (auth/reset)
- `activo`: solo gestionable por ADMIN vía `/api/admin/usuarios/{id}/status`

Los campos PII (dni, cbu, alias_cbu) son editables porque el `EncryptedField` del modelo maneja automáticamente el cifrado/descifrado al setearlos.

**Alternativa descartada**: Reusar `UsuarioUpdate` y filtrar campos en el servicio. Esto es frágil — un campo agregado a `UsuarioUpdate` en el futuro podría exponerse accidentalmente en perfil. Schema propio = contrato explícito.

### D3: Modelo Mensaje con self-referential FK para hilos

**Decisión**: Un solo modelo `Mensaje` con `mensaje_padre_id` (self-referential FK). Un mensaje sin `mensaje_padre_id` es el mensaje raíz de un hilo. Las respuestas referencian al mensaje raíz.

```
Mensaje {
  id, tenant_id, remitente_id (FK User), destinatario_id (FK User),
  asunto, cuerpo, mensaje_padre_id (FK Mensaje, nullable),
  leido (bool, default false), created_at, updated_at, deleted_at
}
```

**Alternativa descartada**: Modelo separado `Hilo` + `Mensaje`. Agrega complejidad innecesaria para un caso de uso simple. La self-referential FK es más directa y SQLAlchemy la soporta nativamente con `remote_side`.

### D4: Inbox usa get_current_user sin permiso fino

**Decisión**: Tanto el perfil como el inbox no requieren `require_permission(...)`. Cualquier usuario autenticado puede editar su perfil y usar la mensajería. El acceso está implícito en la autenticación.

**Alternativa descartada**: Crear permisos `perfil:editar` e `inbox:usar`. Agregaría ruido al modelo de permisos sin beneficio real — son capacidades universales para todo usuario autenticado.

### D5: Listado de inbox agrupa por hilo (no lista mensajes individuales)

**Decisión**: `GET /api/inbox` devuelve una lista de "hilos" donde cada hilo es el mensaje raíz (sin `mensaje_padre_id`) más metadata: cantidad de respuestas, última respuesta, estado de lectura. `GET /api/inbox/{id}` devuelve el mensaje raíz y todas sus respuestas ordenadas cronológicamente.

**Alternativa descartada**: Listar todos los mensajes planos. No escala bien cuando un hilo tiene muchas respuestas y dificulta entender el contexto de la conversación.

### D6: MensajeRepository extiende el Repository genérico

**Decisión**: `MensajeRepository` hereda de `Repository[Mensaje]` que ya provee `get`, `list`, `create`, `update`, `soft_delete` con scope de tenant. Solo se agregan queries específicas: `list_threads_for_user(user_id)`, `get_thread(mensaje_id)`.

### D7: Una sola migración Alembic para la tabla mensaje

**Decisión**: Se crea UNA migración Alembic que agrega la tabla `mensaje` con todos sus índices y constraints. La tabla `user` no se modifica.

## Riesgos / Trade-offs

- **[Riesgo] Self-referential FK puede complicar queries recursivas** → **Mitigación**: La profundidad de hilo es plana (un nivel de respuestas). Las queries usan joins simples, no CTE recursivas.
- **[Riesgo] Sin permiso fino, cualquier usuario puede mensajear a cualquier otro** → **Mitigación**: Es el comportamiento deseado según F3.4 y F11.2. La mensajería interna es abierta entre usuarios del tenant.
- **[Riesgo] El schema PerfilUpdate no incluye DNI en la respuesta** → **Mitigación**: El `PerfilResponse` incluye DNI descifrado. El usuario ve sus propios datos PII. La respuesta del admin (`UsuarioResponse`) ya excluye PII por seguridad, lo cual es correcto para vistas administrativas.
- **[Trade-off] email es editable en perfil** → El UniqueConstraint `(email, tenant_id)` del modelo User se aplica; si el usuario pone un email ya registrado, la DB lanza IntegrityError que el servicio captura como 409.

## Migration Plan

1. Crear migración Alembic: `alembic revision --autogenerate -m "add mensaje table"`
2. Verificar que la migración solo crea la tabla `mensaje` (sin alterar `user`)
3. Deploy: migración hacia adelante. Rollback: `alembic downgrade -1` elimina la tabla `mensaje`
4. No hay migración de datos — es una feature nueva sin datos preexistentes

## Open Questions

- Ninguna. El scope está completamente definido por la KB y las reglas de negocio.
