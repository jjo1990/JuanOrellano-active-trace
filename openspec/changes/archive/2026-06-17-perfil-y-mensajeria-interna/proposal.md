## Why

Los usuarios del sistema necesitan editar sus datos personales y bancarios (perfil propio) sin depender del administrador, y necesitan una bandeja de mensajería interna para comunicarse entre roles dentro del sistema — distinta de las comunicaciones salientes a alumnos ya implementadas en C-12. El cierre de sesión explícito ya está implementado en C-03 y se reutiliza sin cambios.

## What Changes

- **Edición de perfil propio**: endpoint `PATCH /api/perfil` que permite a cualquier usuario autenticado editar su nombre, apellidos, DNI, datos bancarios (banco, CBU, alias CBU), regional, email, modalidad de cobro (facturador), legajo y legajo profesional. El CUIL es de solo lectura — no se incluye en el schema de edición.
- **Bandeja de mensajes interna (inbox)**: nuevo modelo `Mensaje` con soporte de hilos. Endpoints para listar hilos recibidos, leer un hilo completo, responder dentro del hilo y crear nuevos mensajes. La mensajería es entre usuarios registrados del sistema — paralela e independiente de las comunicaciones a alumnos (C-12).
- **Cierre de sesión**: reutiliza `POST /api/auth/logout` de C-03 sin modificaciones. Se documenta como parte de esta épica para el frontend.

## Capabilities

### New Capabilities

- `perfil`: Edición del perfil propio por parte de cualquier usuario autenticado. Campos editables: nombre, apellidos, DNI, banco, CBU, alias CBU, regional, email, facturador, legajo, legajo_profesional. CUIL es solo lectura.
- `inbox`: Mensajería interna entre usuarios registrados del sistema con soporte de hilos. Crear mensajes, listar hilos recibidos, leer conversación completa y responder dentro del hilo.

### Modified Capabilities

<!-- No se modifican capabilities existentes. El logout reutiliza C-03 sin cambios. -->

## Impact

- **Modelos**: nuevo modelo `Mensaje` con tabla `mensaje`. El modelo `User` no requiere cambios (ya tiene todos los campos editables). Nueva migración Alembic para la tabla `mensaje`.
- **Schemas Pydantic**: nuevo schema `PerfilUpdate` (excluye CUIL) y schemas para inbox (`MensajeCreate`, `MensajeResponse`, `MensajeListResponse`).
- **Routers**: nuevo router `perfil.py` (`/api/perfil`) y nuevo router `inbox.py` (`/api/inbox`).
- **Servicios**: nuevo `PerfilService` y `MensajeService`.
- **Repositorios**: nuevo `MensajeRepository`.
- **Dependencias**: sin cambios en el sistema de auth/dependencias. Se usa `get_current_user` para identificar al usuario de la sesión.
- **Permisos**: el perfil es accesible por cualquier usuario autenticado (sin permiso fino específico). El inbox también — la mensajería interna no tiene restricción por rol, cualquier usuario puede enviar/recibir.
