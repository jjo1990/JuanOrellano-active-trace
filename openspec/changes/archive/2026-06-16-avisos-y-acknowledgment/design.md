## Context

C-06 (estructura-academica) y C-07 (usuarios-y-asignaciones) construyeron las entidades raíz. El sistema ya tiene RBAC fino. C-15 modela el tablón de avisos institucionales con segmentación por audiencia y confirmación de lectura.

**Restricciones**: modelos nuevos con BaseModelMixin. Router bajo `/api/avisos`. Sin dependencias nuevas. Contadores derivados de AcknowledgmentAviso, nunca denormalizados.

## Goals / Non-Goals

**Goals:**
- Modelos `Aviso` y `AcknowledgmentAviso`.
- `POST /api/avisos` — crear aviso. Guard: `avisos:publicar`.
- `GET /api/avisos` — listar avisos del publicador (COORD/ADMIN ve todos los propios).
- `PUT /api/avisos/{id}` — editar aviso. Guard: `avisos:publicar`.
- `DELETE /api/avisos/{id}` — soft delete. Guard: `avisos:publicar`.
- `GET /api/avisos/visibles` — avisos visibles para el usuario autenticado según RN-20 + RN-18.
- `GET /api/avisos/{id}` — detalle de un aviso.
- `POST /api/avisos/{id}/ack` — acusar recibo (RN-19). Cualquier usuario autenticado.
- Nuevo permiso `avisos:publicar` (COORDINADOR, ADMIN).

**Non-Goals:**
- Sin notificaciones push/email (→ C-12).
- Sin UI frontend (→ C-23).
- Sin adjuntos en avisos.
- Sin analytics avanzados de lectura.

## Decisions

### D1 — Router único `/api/avisos`

Todos los endpoints bajo un solo router. Separación semántica clara: `/api/avisos` para gestión y `/api/avisos/visibles` para consulta del usuario.

### D2 — Segmentación RN-20: filtrado server-side

Al consultar `GET /api/avisos/visibles`, el servicio:
1. Obtiene el `user_id`, roles y asignaciones del usuario.
2. Filtra avisos donde: `activo=true`, dentro de ventana `inicio_en <= now <= fin_en` (RN-18).
3. Aplica RN-20: si `alcance=Global` → incluye; si `PorMateria` y el usuario está asignado a esa materia → incluye; si `PorCohorte` y el usuario está en esa cohorte → incluye; si `PorRol` y el usuario tiene ese rol → incluye.
4. Ordena por `orden ASC` y luego `inicio_en DESC`.

**Alternativa descartada**: filtrar en frontend. Inviable porque expondría avisos de otros tenants/contextos.

### D3 — Contadores derivados, no denormalizados

`total_vistas` y `total_acks` se calculan con `COUNT` sobre `acknowledgment_aviso` cada vez que se consultan. No se almacenan en `aviso`. Esto evita sincronización y es coherente con la KB ("se derivan consultando AcknowledgmentAviso").

### D4 — Acknowledge: un solo registro por usuario por aviso

`POST /api/avisos/{id}/ack` crea un `AcknowledgmentAviso`. Si ya existe, devuelve 200 sin error (idempotente). UNIQUE(aviso_id, usuario_id).

### D5 — Layout

```
backend/app/
├── api/v1/routers/avisos.py
├── services/aviso_service.py
├── schemas/aviso.py
├── repositories/{aviso_repository,acknowledgment_aviso_repository}.py
├── models/{aviso,acknowledgment_aviso}.py
└── tests/{test_aviso_repository,test_aviso_service}.py
```

### D6 — Permiso: `avisos:publicar`

Constante `AVISOS_PUBLICAR = "avisos:publicar"` en action_codes.py. Otorgado a COORDINADOR y ADMIN vía seed de migración.

## Risks / Trade-offs

- **[Contadores con COUNT en cada request]**: puede ser costoso con muchos avisos y acknowledgments → Mitigación: el volumen de avisos es bajo (decenas, no miles). Si escala, se puede cachear.
- **[Filtrado server-side con múltiples queries]**: el filtro RN-20 requiere consultar asignaciones del usuario → Mitigación: se hace en una sola query con JOINs o subconsultas.

## Migration Plan

1. Migración de schema: tablas `aviso` y `acknowledgment_aviso`.
2. Migración de datos: seed de `avisos:publicar` + RolPermiso. Idempotente.
3. Deploy aditivo. Rollback: downgrade + quitar router.

## Open Questions

- ¿Debe el ALUMNO ver avisos? → Sí, si el alcance y rol_destino lo incluyen.
- ¿Los avisos vencidos se borran? → No, soft delete solo por acción explícita. Se ocultan por RN-18.
