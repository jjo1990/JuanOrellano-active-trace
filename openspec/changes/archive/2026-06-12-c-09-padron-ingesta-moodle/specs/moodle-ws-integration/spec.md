## ADDED Requirements

### Requirement: Cliente Moodle Web Services para sync de padrón

El sistema SHALL proveer un cliente async en `integrations/moodle_ws.py` que se conecte a Moodle vía Web Services API para sincronizar usuarios y actividades del curso. SHALL soportar sync nocturna programada y sync on-demand desde la UI.

#### Scenario: Sync on-demand exitosa

- **GIVEN** un tenant con integración Moodle WS configurada (URL del sitio + token WS)
- **WHEN** se ejecuta sync on-demand para una materia
- **THEN** el cliente se conecta a Moodle vía `core_user_get_users_by_field` y `core_enrol_get_enrolled_users`
- **AND** retorna los datos de alumnos del curso mapeados al formato de EntradaPadron
- **AND** se persiste una nueva VersionPadron con los datos sincronizados

#### Scenario: Moodle WS no disponible

- **GIVEN** un tenant con integración Moodle WS configurada
- **WHEN** el servicio de Moodle no responde o responde con error
- **THEN** el sistema retorna error 502 (Bad Gateway)
- **AND** programa un reintento automático (retry con backoff)

#### Scenario: Tenant sin integración Moodle usa fallback manual

- **GIVEN** un tenant sin configuración de Moodle WS
- **WHEN** se intenta sync on-demand
- **THEN** el sistema retorna error con mensaje "Moodle WS no configurado"
- **AND** sugiere usar import manual por archivo

#### Scenario: Nightly sync programada

- **GIVEN** uno o más tenants con Moodle WS configurado
- **WHEN** se ejecuta el cron nocturno (background worker)
- **THEN** el worker itera sobre los tenants y materias con WS configurado
- **AND** ejecuta sync para cada uno, registrando resultados en audit log
- **AND** los errores parciales no detienen la sincronización de otros tenants

#### Scenario: Mapeo de errores Moodle a 502

- **GIVEN** un error de conexión, timeout o autenticación contra Moodle
- **WHEN** ocurre durante una sync
- **THEN** el sistema captura la excepción y la mapea a HTTP 502 con mensaje descriptivo
- **AND** registra el error en audit log con detalle técnico
