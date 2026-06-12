## Why

C-11 completó el análisis de alumnos atrasados, pero el flujo central importar → analizar → **comunicar** está incompleto sin el último eslabón: notificar a los alumnos detectados. C-12 cierra el camino crítico habilitando el envío masivo de comunicaciones con cola asincrónica, preview obligatorio y aprobación humana configurable. Sin esto, el docente tiene los datos pero no puede actuar sobre ellos desde el sistema.

## What Changes

- **Nuevo modelo `Comunicacion`** (E21) con `destinatario` cifrado, máquina de estados RN-15, `lote_id` para agrupación de envíos masivos y timestamp de envío
- **Worker asincrónico de despacho** (`workers/dispatch_worker.py`): loop simple que consume comunicaciones Pendiente, transiciona Pendiente→Enviando→Enviado/Error. Envío de email **mockeado** para MVP (SMTP real es futuro). Soporta plantillas con variables (`{{nombre}}`, `{{materia}}`, etc.)
- **Preview obligatorio (RN-16)**: endpoint que renderiza template con datos reales del alumno y devuelve preview sin persistir
- **Envío masivo con lote**: endpoint que recibe lista de alumnos + template, crea filas `Comunicacion` agrupadas por `lote_id`
- **Aprobación humana (RN-17)**: endpoint con guard `comunicacion:aprobar` que transiciona un lote completo de Pendiente a aprobado (listo para worker). Soporte para aprobación/cancelación individual
- **Endpoints REST**: `/api/comunicaciones/*` con guard `comunicacion:enviar`
- **Migración 011**: tabla `comunicacion`
- **Auditoría**: `COMUNICACION_ENVIAR` (action code ya existe) registra cada envío y cambio de estado

## Capabilities

### New Capabilities

- `comunicaciones-cola-worker`: Cola de comunicaciones con máquina de estados RN-15, preview obligatorio RN-16, aprobación RN-17, worker asincrónico de despacho con plantillas, y endpoints REST bajo `/api/comunicaciones/`

### Modified Capabilities

<!-- No existing capabilities are modified. This is a new domain module. -->

## Impact

- **Nuevos archivos**: `models/comunicacion.py`, `repositories/comunicacion_repository.py`, `services/comunicacion_service.py`, `schemas/comunicacion.py`, `api/v1/routers/comunicaciones.py`, `workers/dispatch_worker.py`, `alembic/versions/011_create_comunicacion.py`
- **Nuevos tests**: `tests/test_comunicacion_modelo.py`, `tests/test_comunicacion_service.py`, `tests/test_comunicacion_router.py`, `tests/test_comunicacion_worker.py`
- **Dependencias existentes**: FK a `tenant`, `usuario`, `materia` — todas ya existen. `EncryptedField` ya implementado en `models/fields.py`. `action_codes.COMUNICACION_ENVIAR` ya existe. Permisos `comunicacion:enviar` y `comunicacion:aprobar` ya sembrados.
- **Migración**: 011 (siguiente disponible, 010 es la última)
- **Sin cambios en modelos existentes**: solo se agrega el nuevo modelo
