## Context

C-12 completa el camino crítico `C-01 → C-02 → ... → C-11 → C-12`. El sistema ya puede importar calificaciones desde el LMS (C-09, C-10) y detectar alumnos atrasados (C-11). Falta la capacidad de comunicarse con esos alumnos. El módulo de comunicaciones es el último eslabón del flujo central del PROFESOR: importar → analizar → **comunicar**.

El proyecto sigue Clean Architecture con capas Router → Service → Repository → Model. La identidad del usuario y su tenant vienen exclusivamente
del JWT verificado. Las reglas duras del proyecto aplican: `extra='forbid'` en schemas, `tenant_id` en cada tabla, soft-delete, PII cifrada con AES-256, RBAC fino `modulo:accion`.

**Dependencias ya existentes y utilizables:**
- `BaseModelMixin` (id, tenant_id, created_at, updated_at, deleted_at)
- `Repository[T]` genérico con scope tenant obligatorio
- `EncryptedField` descriptor para cifrado en reposo
- `action_codes.COMUNICACION_ENVIAR` ya definido
- Permisos `comunicacion:enviar` y `comunicacion:aprobar` ya sembrados en seed
- FK a `user` (enviado_por) y `materia` (materia_id) disponibles

## Goals / Non-Goals

**Goals:**
- Modelo `Comunicacion` con máquina de estados RN-15, `destinatario` cifrado con EncryptedField y `lote_id`
- Preview obligatorio con renderizado de plantilla (RN-16)
- Envío masivo con agrupación por lote (F3.2)
- Aprobación humana por lote o individual (RN-17, F3.3) con guard `comunicacion:aprobar`
- Worker asincrónico que consume Pendiente → Enviando → Enviado/Error
- Endpoints REST bajo `/api/comunicaciones/` con guard `comunicacion:enviar`
- Auditoría con `COMUNICACION_ENVIAR` en cada envío
- Tests con TDD estricto (≥80% líneas, ≥90% reglas de negocio)

**Non-Goals:**
- Integración SMTP real — el envío de email se mockea para MVP
- Plantillas guardadas en DB — para MVP se pasan inline en el request
- UI de administración de plantillas
- Programación de envíos diferidos (solo inmediato)
- Integración con N8N para el dispatch (futuro)

## Decisions

### 1. Modelo `Comunicacion` con `EncryptedField` para `destinatario`

**Qué**: `destinatario` usa el descriptor `EncryptedField` igual que `EntradaPadron.email` y los campos PII de `User`.

```python
class Comunicacion(BaseModelMixin, Base):
    __tablename__ = "comunicacion"

    # tenant_id se hereda de BaseModelMixin (no se redeclara)
    enviado_por: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("user.id"), nullable=False,
    )
    materia_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("materia.id"), nullable=False,
    )
    destinatario_encrypted = mapped_column(String(512), nullable=False)
    destinatario = EncryptedField()
    asunto: Mapped[str] = mapped_column(String(500), nullable=False)
    cuerpo: Mapped[str] = mapped_column(Text, nullable=False)
    estado: Mapped[str] = mapped_column(String(20), nullable=False)
    lote_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    lote_aprobado: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    enviado_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True), nullable=True)
```

Check constraints:
- `estado` IN `('Pendiente', 'Enviando', 'Enviado', 'Error', 'Cancelado')`. `Pendiente` es el default al crear.

**Por qué**: EncryptedField ya existe, está probado, y `destinatario` contiene email que es PII según las reglas del proyecto.

### 2. Máquina de estados RN-15 con función `validate_transition()`

**Qué**: Función pura que recibe `(estado_actual, estado_nuevo) → bool`.

```
Pendiente → Enviando   ✓  (worker toma el mensaje)
Pendiente → Cancelado  ✓  (cancelación antes de dispatch)
Enviando  → Enviado    ✓  (despacho exitoso)
Enviando  → Error      ✓  (fallo en despacho)
Cualquier otra         ✗  (transición inválida)
```

No existen transiciones desde `Enviado`, `Error` o `Cancelado` — son estados terminales.

**Por qué**: Función pura, testeable unitariamente sin DB. El service llama a `validate_transition()` como guard antes de cualquier cambio de estado. Lanza `ValueError` descriptivo si es inválida.

**Alternativa considerada**: Enum con métodos de transición. Descartada porque acopla la lógica al ORM y dificulta el testeo unitario.

### 3. Worker como loop asincrónico simple (no Celery)

**Qué**: `dispatch_worker.py` es un script que corre como proceso separado (ya previsto en `docker-compose.yml`). Es un `while True` con `asyncio.sleep()` que:
1. Consulta `Comunicacion` con `estado='Pendiente'` (batch de N)
2. Para cada una: transiciona a `Enviando`, llama a `_send_email()`, transiciona a `Enviado` o `Error`
3. Duerme X segundos y repite

```python
async def run_worker(session_factory, poll_interval=5, batch_size=10):
    while True:
        async with session_factory() as db:
            # Solo Pendiente con lote aprobado o sin lote (envíos individuales)
            pendientes = await repo.get_pendientes(limit=batch_size)
            for c in pendientes:
                try:
                    validate_transition(c.estado, "Enviando")  # guard D2
                    c.estado = "Enviando"
                    await db.commit()
                    _send_email(c.destinatario, c.asunto, c.cuerpo)
                    validate_transition(c.estado, "Enviado")
                    c.estado = "Enviado"
                    c.enviado_at = datetime.now(timezone.utc)
                except ValueError:
                    logger.error("Transición inválida para comunicación %s (estado=%s)", c.id, c.estado)
                except Exception:
                    c.estado = "Error"
                await db.commit()
        await asyncio.sleep(poll_interval)
```

**Por qué**: El proyecto ya tiene la carpeta `workers/` prevista y un servicio worker en docker-compose. No necesitamos Celery para una cola simple de emails — sería sobre-ingeniería para MVP. Además, la regla dura dice "sin dependencias que compliquen el deploy" y Celery requiere broker (Redis/RabbitMQ).

**Alternativa considerada**: Celery + Redis. Descartada por complejidad de infraestructura innecesaria para MVP. Se puede migrar a futuro sin cambiar el modelo de datos.

### 4. Envío de email mockeado para MVP

**Qué**: `_send_email(destinatario, asunto, cuerpo)` es una función que **loguea** el email y devuelve `True` (éxito simulado). No se conecta a ningún SMTP.

```python
def _send_email(destinatario: str, asunto: str, cuerpo: str) -> bool:
    logger.info("EMAIL_SIMULATED", extra={
        "to": destinatario, "subject": asunto, "body_length": len(cuerpo),
    })
    return True
```

Para forzar fallos en tests: se puede mockear `_send_email` para que lance excepción.

**Por qué**: SMTP real requiere configuración de tenant (servidor, credenciales, puerto) que es un change separado. El MVP necesita que el flujo de estados funcione end-to-end; el envío real es transparente al modelo de datos y la UI.

### 5. Plantillas con variables de sustitución

**Qué**: Las plantillas usan sintaxis `{{variable}}`. Variables soportadas:
- `{{nombre}}` — nombre completo del alumno
- `{{materia}}` — nombre de la materia
- `{{actividades_pendientes}}` — lista de actividades faltantes
- `{{nota_promedio}}` — nota promedio del alumno
- `{{link_materia}}` — URL al aula virtual (placeholder para futuro)

La renderización ocurre en el service: `render_template(template: str, context: dict) -> str`. Usa `re.sub(r'\{\{(\w+)\}\}', lambda m: context.get(m.group(1), m.group(0)), template)` para evitar reemplazos parciales (ej: `{{nombre}}` no matchea `{{nombre_completo}}`). Reemplazable por Jinja2 en futuro.

**Por qué**: MVP necesita personalización básica. Jinja2 sería sobre-ingeniería para las 5 variables actuales. `re.sub()` es trivial, testeable, no agrega dependencia, y evita el bug de `str.replace()` donde `{{nombre}}` matchearía parcialmente `{{nombre_completo}}`.

**Alternativa considerada**: Jinja2. Descartada para MVP pero el método `render_template()` está diseñado para que sea drop-in reemplazo.

### 6. Endpoints REST

| Método | Path | Permiso | Descripción |
|--------|------|---------|-------------|
| `POST` | `/api/comunicaciones/preview` | `comunicacion:enviar` | Renderiza template con datos reales, devuelve preview (no persiste) |
| `POST` | `/api/comunicaciones/enviar` | `comunicacion:enviar` | Envía en lote: recibe alumnos + template, crea filas con `lote_id` |
| `GET` | `/api/comunicaciones/lote/{lote_id}` | `comunicacion:enviar` | Estado de un lote (todas las comunicaciones del lote) |
| `GET` | `/api/comunicaciones/materia/{materia_id}` | `comunicacion:enviar` | Comunicaciones de una materia (filtrable por estado) |
| `POST` | `/api/comunicaciones/aprobar/{lote_id}` | `comunicacion:aprobar` | Aprueba todo un lote → listo para worker |
| `POST` | `/api/comunicaciones/aprobar/{lote_id}/comunicacion/{id}` | `comunicacion:aprobar` | Aprueba/cancela una comunicación individual del lote |
| `POST` | `/api/comunicaciones/cancelar/{id}` | `comunicacion:enviar` | Cancela comunicación individual Pendiente (solo dueño o `comunicacion:aprobar`) |

**Nota**: El preview NO persiste en DB. Recibe los mismos parámetros que `enviar` pero devuelve el contenido renderizado para confirmación del usuario.

### 7. Flujo de aprobación RN-17

1. Profesor crea lote vía `POST /api/comunicaciones/enviar` → todas quedan `Pendiente`
2. Worker NO procesa Pendientes que pertenecen a un lote **hasta que el lote esté aprobado**
3. Coordinador/Admin aprueba vía `POST /api/comunicaciones/aprobar/{lote_id}` → worker ya puede consumirlas
4. Alternativa: cancelar lote completo → todas pasan a `Cancelado`
5. Alternativa: aprobar/cancelar individualmente dentro del lote

**Implementación**: Worker consulta solo `Pendiente AND (lote_id IS NULL OR lote_aprobado = true)`. Para simplificar MVP, el campo de aprobación se modela con una tabla/flag adicional (ver Open Questions).

### 8. Tenant isolation

Como todo modelo del sistema, `Comunicacion` tiene `tenant_id` y el `ComunicacionRepository` hereda de `Repository[Comunicacion]` que filtra por tenant por defecto. Sin cambios arquitectónicos.

### 9. Migración 011

Schema de tabla `comunicacion` con:
- `id UUID PK DEFAULT gen_random_uuid()`
- `tenant_id UUID NOT NULL FK → tenant`
- `enviado_por UUID NOT NULL FK → user`
- `materia_id UUID NOT NULL FK → materia`
- `destinatario_encrypted VARCHAR(512) NOT NULL`
- `asunto VARCHAR(500) NOT NULL`
- `cuerpo TEXT NOT NULL`
- `estado VARCHAR(20) NOT NULL DEFAULT 'Pendiente'` + check constraint `IN ('Pendiente','Enviando','Enviado','Error','Cancelado')`
- `lote_id UUID`
- `lote_aprobado BOOLEAN NOT NULL DEFAULT FALSE`
- `enviado_at TIMESTAMP WITH TIME ZONE`
- `created_at`, `updated_at`, `deleted_at` (de BaseModelMixin)

Índices:
- `ix_comunicacion_estado` en `(tenant_id, estado)` — para el worker
- `ix_comunicacion_lote` en `(lote_id)` — para queries de estado de lote
- `ix_comunicacion_materia` en `(tenant_id, materia_id)` — para vista por materia

## Risks / Trade-offs

- **[Worker sin supervisor]**: Si el worker crashea, los mensajes quedan en `Enviando` sin procesar. → Mitigación: worker marca `Enviando` + timestamp; un health-check periódico puede rescatar `Enviando` > timeout y volverlos a `Pendiente`. Para MVP se documenta como known limitation.
- **[Mock email sin reintentos]**: Si `_send_email` falla, el mensaje va directo a `Error`. → Mitigación: el modelo soporta reintento manual (cambiar estado a `Pendiente`), pero MVP no incluye reintento automático.
- **[Aprobación de lote sin tabla separada]**: La columna `lote_aprobado` en `comunicacion` resuelve RN-17 para MVP. Si a futuro la lógica de aprobación se complejiza (múltiples aprobadores, historial de aprobaciones), se migra a tabla `AprobacionLote` separada.
- **[Template rendering con regex]**: `re.sub(r'\{\{(\w+)\}\}', ...)` evita reemplazos parciales y es inmune a inyección porque solo acepta `\w+` como nombre de variable. Si se migra a Jinja2, el autoescaping protege adicionalmente.

## Open Questions

1. **Flag de aprobación de lote**: ✅ **Resuelto.** Columna `lote_aprobado BOOLEAN DEFAULT FALSE` en la tabla `comunicacion`. El endpoint `POST /aprobar/{lote_id}` hace un batch update `SET lote_aprobado = true` sobre todas las comunicaciones del lote. El worker consulta solo `Pendiente AND (lote_id IS NULL OR lote_aprobado = true)`.

2. **Worker startup en Docker**: ✅ **Resuelto.** Misma imagen que la API, entrypoint diferente: `python -m app.workers.dispatch_worker`. Comparte el Dockerfile multi-stage existente en `backend/Dockerfile`. El servicio `worker` en `docker-compose.yml` ya existe como placeholder.
