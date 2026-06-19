## Why

El backend de activia-trace está operativo desde sus cimientos (C-01 a C-04) — autenticación, multi-tenancy, RBAC y auditoría — pero no existe ningún frontend. Los usuarios no tienen forma de autenticarse ni navegar el sistema desde una interfaz gráfica. Este change construye el shell SPA y el flujo de autenticación completo, la puerta de entrada a todas las features de frontend que le siguen (C-22, C-23, C-24).

## What Changes

- **Scaffolding** de proyecto React 18 + TypeScript + Vite con estructura feature-based según `docs/ARQUITECTURA.md §4`.
- **Cliente HTTP centralizado** en `@/shared/services/api.ts` con instancia Axios configurada: baseURL desde env, interceptor JWT, refresh transparente ante 401, manejo de 403.
- **Contexto de sesión** (AuthContext): almacena tokens en memoria, provee estado de autenticación a toda la app.
- **Pantallas de auth**: Login (email + password), 2FA (TOTP code gate), recuperación de contraseña (forgot → email enviado → reset con token). Consumen los endpoints existentes de C-03.
- **Route guard**: rutas protegidas redirigen a login si no hay sesión; rutas públicas (login, forgot-password, reset-password) redirigen al shell si ya hay sesión.
- **Shell de aplicación**: layout con sidebar responsive, navegación adaptada a los roles del usuario (los items visibles dependen de los permisos de la sesión).
- **Logout**: cierre de sesión explícito que invalida tokens en backend y limpia estado local.
- **Tests**: render de pantallas de auth, flujo completo de login/logout con API mockeada, redirección del guard sin sesión, refresh transparente de tokens.

## Capabilities

### New Capabilities
- `auth-screen`: Pantallas de login, 2FA (TOTP challenge gate) y recuperación de contraseña (forgot → reset). Cada pantalla consume los endpoints correspondientes de C-03 vía el cliente HTTP centralizado.
- `http-client`: Instancia Axios con interceptor de JWT, refresh rotation transparente (401 → refresh → retry original), manejo de errores 403, y header de tenant automático. Almacenamiento de tokens exclusivamente en memoria (AuthContext).
- `route-guard`: Lógica de protección de rutas. Routes públicas (login, forgot, reset) accesibles sin sesión. Routes protegidas redirigen a /login si no hay sesión. Routes con permiso requerido muestran 403 si el usuario no lo tiene. Usuario autenticado en ruta pública redirige al shell.
- `app-shell`: Layout principal post-login con sidebar de navegación responsive, header con info de usuario y logout, área de contenido con Outlet de React Router. Menú de navegación se construye dinámicamente según los permisos del usuario (roles determinan qué items se muestran).

### Modified Capabilities
<!-- No existing frontend specs to modify. This is greenfield. -->

## Impact

- **Nuevo directorio**: `frontend/` completo (package.json, vite.config.ts, tsconfig.json, tailwind.config, src/ con estructura feature-based).
- **Nuevas dependencias npm**: react, react-dom, react-router-dom, @tanstack/react-query, react-hook-form, zod, @hookform/resolvers, axios, tailwindcss, vite, vitest, @testing-library/react, msw.
- **Consume API backend**: `POST /api/auth/login`, `POST /api/auth/login/2fa`, `POST /api/auth/refresh`, `POST /api/auth/logout`, `POST /api/auth/forgot`, `POST /api/auth/reset`, `GET /api/health`.
- **No modifica backend**: es puramente frontend, consumiendo los contratos de API ya establecidos en C-03.
