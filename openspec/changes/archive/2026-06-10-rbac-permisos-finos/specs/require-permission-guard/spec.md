## ADDED Requirements

### Requirement: require_permission como FastAPI dependency
El sistema SHALL proveer una función `require_permission(permiso: str)` que retorna una FastAPI dependency. La dependency obtiene el current_user, resuelve sus permisos efectivos vía `PermissionService`, y si no tiene el permiso → HTTPException 403.

#### Scenario: Usuario con permiso pasa el guard
- **WHEN** un usuario tiene el permiso `calificaciones:importar` en sus permisos efectivos
- **AND** la dependency `require_permission("calificaciones:importar")` se ejecuta
- **THEN** no se lanza excepción

#### Scenario: Usuario sin permiso recibe 403
- **WHEN** un usuario NO tiene el permiso `calificaciones:importar` en sus permisos efectivos
- **AND** la dependency `require_permission("calificaciones:importar")` se ejecuta
- **THEN** se lanza `HTTPException(status_code=403, detail="Permiso requerido: calificaciones:importar")`

#### Scenario: Token invalido recibe 401 (antes del permiso)
- **WHEN** no hay token válido
- **AND** la dependency `require_permission(...)` se ejecuta
- **THEN** se lanza `HTTPException(status_code=401)` por `get_current_user` antes de llegar al chequeo de permiso

### Requirement: Context check para permisos (propio)
El sistema SHALL soportar un callback opcional de verificación de contexto en `require_permission` para permisos marcados como `(propio)`.

#### Scenario: Context check pasa
- **WHEN** un PROFESOR usa `require_permission("calificaciones:importar", context_check=lambda user, resource: resource.owner_id == user.id)`
- **AND** el recurso le pertenece
- **THEN** el guard permite el acceso

#### Scenario: Context check falla
- **WHEN** un PROFESOR usa `require_permission("calificaciones:importar", context_check=lambda user, resource: resource.owner_id == user.id)`
- **AND** el recurso NO le pertenece
- **THEN** se lanza `HTTPException(status_code=403)`

### Requirement: Decorador a nivel de endpoint
El sistema SHALL permitir usar `require_permission` como dependency en routers y decoradores de endpoints.

#### Scenario: Endpoint declarativo con require_permission
- **WHEN** se declara `@router.get("/calificaciones", dependencies=[Depends(require_permission("calificaciones:importar"))])`
- **THEN** la ruta está protegida

### Requirement: Sin permiso declarado = fail-closed (futuro)
Los endpoints protegidos DEBEN declarar explícitamente el permiso requerido. Por ahora, el sistema no impone un middleware global — cada endpoint debe declarar su `require_permission` explícitamente.

#### Scenario: Endpoint sin permiso declarado no tiene proteccion
- **WHEN** un endpoint NO usa `require_permission`
- **THEN** cualquier usuario autenticado puede acceder (comportamiento actual, a migrar progresivamente)
