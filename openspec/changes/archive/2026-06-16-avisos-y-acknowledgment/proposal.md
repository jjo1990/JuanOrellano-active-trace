## Why

El sistema ya tiene comunicación saliente a alumnos (C-12) y mensajería interna (C-20 pendiente), pero no existe un mecanismo de notificaciones institucionales segmentadas: avisos que el COORDINADOR publica para grupos específicos de usuarios según alcance, rol, materia y cohorte, con ventana de vigencia y confirmación de lectura obligatoria. Sin los modelos `Aviso` y `AcknowledgmentAviso`, los docentes no tienen un tablón de anuncios y la coordinación no puede asegurar que las comunicaciones críticas fueron leídas.

## What Changes

- **F3.5 — Tablón de avisos**: ABM de avisos con alcance (Global/PorMateria/PorCohorte/PorRol), severidad (Info/Advertencia/Crítico), vigencia (inicio/fin según RN-18), orden de prioridad, y opción de requerir acuse de recibo (RN-19).
- **RN-20 — Segmentación por audiencia**: cada aviso define su audiencia por combinación de alcance, materia_id, cohorte_id, rol_destino y severidad. El sistema filtra automáticamente qué avisos ve cada usuario según su rol, asignaciones y cohorte.
- **RN-18 — Ventana de vigencia**: los avisos solo son visibles dentro de su rango `inicio_en`/`fin_en`. Fuera de ese rango no se muestran aunque sigan existiendo.
- **RN-19 — Acuse de recibo**: endpoint `POST /api/avisos/{id}/ack` para que un usuario confirme lectura. Si `requiere_ack=true`, el aviso se sigue mostrando hasta que el usuario acuse. Contadores de vistas y acuses derivados de `AcknowledgmentAviso` (nunca denormalizados).
- **Nuevo modelo `Aviso`**: alcance, materia_id, cohorte_id, rol_destino, severidad, título, cuerpo, inicio_en, fin_en, orden, activo, requiere_ack.
- **Nuevo modelo `AcknowledgmentAviso`**: aviso_id, usuario_id, confirmado_at.
- **Nuevo permiso**: `avisos:publicar` (COORDINADOR, ADMIN).
- **Nueva migración Alembic**: tablas `aviso` y `acknowledgment_aviso` + seed de permiso.

## Capabilities

### New Capabilities

- `avisos-crud`: ABM de avisos con todos los campos de segmentación, vigencia y severidad. Guard: `avisos:publicar`.
- `avisos-visualizacion`: consulta de avisos visibles para el usuario autenticado según RN-20 (filtrado por rol, asignaciones, cohorte). Solo dentro de ventana de vigencia (RN-18). Ordenados por prioridad.
- `avisos-acknowledgment`: confirmación de lectura de avisos que requieren acuse (RN-19). Contadores derivados de la tabla `acknowledgment_aviso`.

### Modified Capabilities

Ninguna.

## Impact

- **Nuevo código**: `models/aviso.py`, `models/acknowledgment_aviso.py`, `schemas/aviso.py`, `api/v1/routers/avisos.py`, `services/aviso_service.py`, `repositories/aviso_repository.py`, `repositories/acknowledgment_aviso_repository.py`.
- **Modificado**: `models/__init__.py`, `core/action_codes.py`, `main.py`.
- **Nuevo permiso**: `avisos:publicar` vía migración de datos.
- **Migración**: nueva migración Alembic con tablas `aviso` y `acknowledgment_aviso`.
- **Dependencia**: C-06 (`Materia`, `Cohorte`) y C-07 (`User`). Sin cambios en modelos existentes.
- **Governance**: MEDIO — lógica de dominio con reglas de negocio documentadas, sin datos PII.
