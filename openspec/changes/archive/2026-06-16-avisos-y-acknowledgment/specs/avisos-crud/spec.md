## ADDED Requirements

### Requirement: Crear aviso
El sistema SHALL permitir a COORDINADOR/ADMIN crear avisos con alcance, segmentación, vigencia y severidad (F3.5).

#### Scenario: Crear aviso global con acuse
- **WHEN** un COORDINADOR envía `POST /api/avisos` con alcance=Global, severidad=Critico, titulo, cuerpo, inicio_en, fin_en, requiere_ack=true
- **THEN** el sistema crea el aviso con estado activo

#### Scenario: Crear aviso por materia con rol destino
- **WHEN** un COORDINADOR envía `POST /api/avisos` con alcance=PorMateria, materia_id, rol_destino=PROFESOR
- **THEN** el sistema crea el aviso segmentado

#### Scenario: Crear aviso sin permiso
- **WHEN** un PROFESOR envía `POST /api/avisos`
- **THEN** el sistema responde 403

### Requirement: Listar avisos del publicador
El sistema SHALL listar los avisos creados por el publicador (COORDINADOR/ADMIN).

#### Scenario: COORDINADOR lista sus avisos
- **WHEN** un COORDINADOR envía `GET /api/avisos`
- **THEN** el sistema devuelve todos los avisos del tenant con contadores de vistas y acuses

### Requirement: Editar aviso
El sistema SHALL permitir modificar un aviso existente (campos editables: todos excepto id).

#### Scenario: Desactivar aviso
- **WHEN** un COORDINADOR envía `PUT /api/avisos/{id}` con activo=false
- **THEN** el aviso deja de mostrarse a los usuarios aunque esté en ventana

### Requirement: Soft delete aviso
El sistema SHALL implementar soft delete para avisos.

#### Scenario: Eliminar aviso
- **WHEN** un ADMIN envía `DELETE /api/avisos/{id}`
- **THEN** el sistema marca deleted_at y el aviso deja de aparecer en cualquier listado

### Requirement: Aislamiento multi-tenant
El sistema SHALL aislar los avisos por tenant.

#### Scenario: Avisos de otro tenant no visibles
- **WHEN** un usuario de tenant A consulta avisos
- **THEN** solo ve avisos del tenant A
