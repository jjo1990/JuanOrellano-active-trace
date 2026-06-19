## Why

C-07 construyó las asignaciones de docentes a materias, pero el sistema aún no tiene representación de las actividades sincrónicas que esos docentes realizan: clases virtuales, encuentros recurrentes y guardias de atención a alumnos. Sin los modelos `SlotEncuentro`, `InstanciaEncuentro` y `Guardia`, el coordinador no puede supervisar qué encuentros se dieron, el docente no puede registrar grabaciones, y los alumnos no pueden acceder al calendario de clases desde el aula virtual. Este change cierra esa brecha modelando el dominio completo de encuentros y guardias (Épica 6).

## What Changes

- **F6.1 — Crear encuentro recurrente**: endpoint `POST /api/encuentros/slots` que define un slot con día de semana, horario, fecha de inicio y cantidad de semanas. El sistema genera automáticamente N instancias (`InstanciaEncuentro`) según RN-13. Guard: `encuentros:gestionar` (PROFESOR, COORDINADOR).
- **F6.2 — Crear encuentro único**: endpoint `POST /api/encuentros/instancias` que crea una instancia independiente (sin slot padre) para una fecha y hora específicas. Guard: `encuentros:gestionar`.
- **F6.3 — Editar instancia de encuentro**: endpoint `PUT /api/encuentros/instancias/{id}` para modificar estado, meet_url, video_url y comentario de una instancia individual (RN-14: el estado es independiente del slot). Guard: `encuentros:gestionar`.
- **F6.4 — Generar bloque HTML para aula virtual**: endpoint `GET /api/encuentros/slots/{id}/aula-virtual` que devuelve un fragmento HTML con el calendario de encuentros y grabaciones listo para publicar en el LMS.
- **F6.5 — Vista admin de encuentros**: endpoint `GET /api/encuentros/admin` para que COORDINADOR/ADMIN auditen transversalmente todos los encuentros del tenant. Guard: `encuentros:gestionar`.
- **F6.6 — Registro de guardias**: endpoints CRUD para `Guardia`: `POST /api/guardias` (registrar guardia cubierta por TUTOR), `GET /api/guardias` (consulta filtrada por materia/carrera/cohorte), `GET /api/guardias/exportar` (exportación CSV). Guard: `guardias:registrar` para escritura (TUTOR); consulta global para COORDINADOR/ADMIN.
- **Nuevos modelos SQLAlchemy**: `SlotEncuentro`, `InstanciaEncuentro`, `Guardia` con `BaseModelMixin` (soft delete, timestamps, tenant_id).
- **Nuevos permisos**: `encuentros:gestionar` (PROFESOR, COORDINADOR) y `guardias:registrar` (TUTOR, COORDINADOR, ADMIN).
- **Nueva migración Alembic**: tablas `slot_encuentro`, `instancia_encuentro`, `guardia` + seed de permisos.

## Capabilities

### New Capabilities

- `slots-encuentro`: CRUD de slots de encuentro con dos modos (recurrente y único) según RN-13. Incluye endpoint de generación de bloque HTML para el aula virtual (F6.4).
- `instancias-encuentro`: gestión individual de instancias derivadas de slots o independientes. Cada instancia tiene estado propio (Programado, Realizado, Cancelado) según RN-14. Edición de meet_url, video_url y comentario (F6.3).
- `guardias`: registro y consulta de guardias cubiertas por tutores. CRUD con filtros por materia, carrera y cohorte. Exportación CSV. Consulta global para coordinación (F6.6).
- `vista-admin-encuentros`: consulta transversal de todos los encuentros del tenant para supervisión de coordinación (F6.5).

### Modified Capabilities

Ninguna — este change introduce capacidades nuevas sin modificar specs existentes.

## Impact

- **Nuevo código**: `models/slot_encuentro.py`, `models/instancia_encuentro.py`, `models/guardia.py`, `schemas/encuentro.py`, `schemas/guardia.py`, `api/v1/routers/encuentros.py`, `api/v1/routers/guardias.py`, `services/encuentro_service.py`, `services/guardia_service.py`, `repositories/slot_encuentro_repository.py`, `repositories/instancia_encuentro_repository.py`, `repositories/guardia_repository.py`.
- **Modificado**: `models/__init__.py` (exports), `core/security.py` o migración de seed (nuevos permisos).
- **Nuevos permisos**: `encuentros:gestionar` y `guardias:registrar` (migración de datos para insertar permisos + RolPermiso).
- **Migración**: nueva migración Alembic que crea las tablas `slot_encuentro`, `instancia_encuentro`, `guardia` con FK a `materia`, `asignacion`, `carrera`, `cohorte` y `slot_encuentro`.
- **Dependencia**: C-07 (`Asignacion` como FK para slots y guardias, `Materia`, `Carrera`, `Cohorte` de C-06). Sin cambios en modelos existentes.
- **Habilita**: C-23 `frontend-coordinacion` (necesita endpoints de encuentros y guardias para la UI de coordinación).
- **Governance**: MEDIO — lógica de dominio con reglas de negocio (RN-13, RN-14), sin datos PII ni operaciones financieras.
