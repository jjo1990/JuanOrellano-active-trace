## ADDED Requirements

### Requirement: PermissionService resuelve permisos efectivos
El sistema SHALL proveer `PermissionService` que dado un `user_id` y `tenant_id` resuelve el set de permisos efectivos como unión de permisos de todos los roles del usuario, acotado por tenant y vigencia de asignación.

#### Scenario: Permisos efectivos incluyen union de roles
- **WHEN** un usuario tiene roles PROFESOR y COORDINADOR
- **THEN** `PermissionService.get_effective_permissions(user_id, tenant_id)` retorna la unión de permisos de ambos roles

#### Scenario: Permisos excluyen roles vencidos
- **WHEN** un usuario tiene una asignación `usuario_rol` con `fecha_hasta` en el pasado
- **THEN** los permisos de ese rol NO se incluyen en los permisos efectivos

#### Scenario: Permisos incluyen roles con fecha_hasta null
- **WHEN** un usuario tiene una asignación `usuario_rol` con `fecha_hasta` NULL
- **THEN** los permisos de ese rol SÍ se incluyen (vigencia abierta)

#### Scenario: Permisos excluyen tenant ajeno
- **WHEN** se resuelven permisos para user_id del tenant A en el contexto del tenant B
- **THEN** no se devuelve ningún permiso (fail-closed)

#### Scenario: Servicio no cachea resultados entre requests
- **WHEN** se llama dos veces a `PermissionService.get_effective_permissions`
- **THEN** cada llamada consulta la base de datos (sin caché)

### Requirement: Slim down del JWT
Los roles NO deben viajar en el JWT. Se resuelven server-side vía `PermissionService` en cada request autenticado.

#### Scenario: JWT no contiene roles
- **WHEN** se genera un access token
- **THEN** el payload NO incluye el claim `roles`
- **AND** `get_current_user` no popula roles desde el token

#### Scenario: Roles existen solo en DB
- **WHEN** se verifica un token
- **THEN** `UserInfo.roles` se resuelve desde `usuario_rol` en DB, no desde el JWT
