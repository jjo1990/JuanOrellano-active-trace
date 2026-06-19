## Context

activia-trace tiene backend operativo hasta C-04 (auth JWT + 2FA + RBAC). El frontend es greenfield: no existe `frontend/`. Este change construye la SPA desde cero con el stack definido en `docs/ARQUITECTURA.md §2` y la estructura feature-based de `docs/ARQUITECTURA.md §4`.

Los endpoints de auth que consumiremos están implementados en `backend/app/api/v1/routers/auth.py` y sus schemas en `backend/app/schemas/auth.py`. El contrato es:

| Endpoint | Request Body | Response |
|----------|-------------|----------|
| `POST /api/auth/login` | `{email, password}` | `{access_token, refresh_token}` o `{requires_2fa: true, challenge_token}` |
| `POST /api/auth/login/2fa` | `{challenge_token, totp_code}` | `{access_token, refresh_token}` |
| `POST /api/auth/refresh` | `{refresh_token}` (requiere auth header) | `{access_token, refresh_token}` |
| `POST /api/auth/logout` | `{refresh_token}` (requiere auth header) | `{message}` |
| `POST /api/auth/forgot` | `{email}` | `{message}` |
| `POST /api/auth/reset` | `{token, new_password}` | `{message}` |
| `GET /api/health` | — | `{status: "ok"}` |

El backend exige header `X-Tenant-Id` en toda request. El frontend lo obtiene del subdominio o variable de entorno (`VITE_TENANT_ID`). El JWT tiene claims: `user_id`, `tenant_id`, `roles`, `exp`. Los permisos se resuelven server-side — el frontend no replica la matriz RBAC.

## Goals / Non-Goals

**Goals:**
- Scaffold completo del proyecto frontend con Vite, React 18, TypeScript estricto, Tailwind CSS, TanStack Query, React Hook Form + Zod, Axios.
- Cliente HTTP con interceptor JWT, refresh rotation transparente, y manejo de errores 401/403.
- Pantallas de auth funcionales contra el backend real: login, 2FA gate, forgot password, reset password.
- Route guard que protege rutas por autenticación y permisos.
- App shell con sidebar responsive y menú adaptado a permisos.
- Logout que limpia sesión local e invalida en backend.
- Tests con Vitest + React Testing Library + MSW para mockear API.

**Non-Goals:**
- No implementa features de dominio (calificaciones, atrasados, equipos, etc.) — eso es C-22, C-23, C-24.
- No implementa el portal del alumno (Moodle SSO) — es Fase 2.
- No implementa impersonation UI — se expone endpoint pero sin pantalla en esta iteración.
- No gestiona roles/permissions del lado del frontend más allá de ocultar/mostrar items de menú.
- No tiene i18n en esta iteración.

## Decisions

### D1: JWT en memoria (AuthContext), no en localStorage

**Decisión**: Los tokens (access + refresh) se almacenan exclusivamente en un React Context en memoria. No persisten en localStorage ni sessionStorage.

**Alternativas consideradas**:
- localStorage: vulnerable a XSS — cualquier script en la página puede leer el token.
- httpOnly cookie: requeriría que el backend setee la cookie, pero el backend actual usa `Authorization: Bearer`. Cambiar el contrato de auth es scope de backend.
- sessionStorage: mismo problema que localStorage, solo que se limpia al cerrar tab.

**Racional**: Memoria es la opción más segura para SPA con backend que no setea cookies httpOnly. El refresh token permite re-autenticación silenciosa tras recargar la página si el refresh token sigue vigente... pero en memoria, un reload pierde todo. **Compensación**: al recargar la página, si el access token expiró y el refresh token se perdió, el usuario vuelve a login. Es aceptable para el MVP dado que los tokens son de 15 min.

### D2: React Router v6 con layout route

**Decisión**: Usar React Router v6 con un layout route anidado:

```
<Routes>
  <Route element={<PublicGuard />}>        {/* redirige a /app si hay sesión */}
    <Route path="/login" element={<LoginPage />} />
    <Route path="/forgot-password" element={<ForgotPasswordPage />} />
    <Route path="/reset-password" element={<ResetPasswordPage />} />
  </Route>
  <Route element={<AuthGuard />}>           {/* redirige a /login si no hay sesión */}
    <Route element={<AppShell />}>          {/* layout con sidebar + outlet */}
      <Route path="/app" element={<DashboardPage />} />
      <Route path="/app/unauthorized" element={<UnauthorizedPage />} />
      {/* features futuras (C-22, C-23, C-24) agregan rutas aquí */}
    </Route>
  </Route>
  <Route path="*" element={<Navigate to="/login" />} />
</Routes>
```

**Alternativas consideradas**:
- TanStack Router: demasiado nuevo, curva de aprendizaje innecesaria para este scope.
- Next.js: overkill — no necesitamos SSR/SSG; el producto es una SPA pura tras login.

### D3: Axios interceptor único con queue de refresh

**Decisión**: Un interceptor de response en la instancia Axios que:
1. Adjunta `Authorization: Bearer <access_token>` a toda request (desde AuthContext, inyectado vía módulo).
2. Ante 401, intenta refresh con el refresh token.
3. Si el refresh está en curso, encola las requests concurrentes y las re-despacha con el nuevo token.
4. Si el refresh falla (401/400), limpia la sesión y redirige a `/login`.
5. Ante 403, redirige a `/app/unauthorized`.
6. Ante errores de red (sin respuesta), muestra toast de error genérico.

**Alternativas consideradas**:
- fetch nativo: no tiene interceptores nativos; hay que wrappear todo.
- react-query con retry: no resuelve el refresh transparente; necesitamos reinyectar el token.
- axios-auth-refresh (lib): agrega dependencia para algo trivial (~30 líneas).

**Racional**: Implementación propia mínima (~50 LOC) que queda bajo control del equipo.

### D4: TanStack Query para TODO fetch al backend

**Decisión**: Toda llamada API se hace a través de hooks de TanStack Query (`useQuery` para GETs, `useMutation` para POST/PUT/DELETE). Los hooks viven en `features/<domain>/services/` y usan la instancia Axios centralizada.

**Racional**: Caching, refetch en focus, estados de loading/error unificados, y retry automático. Es el estándar definido en `docs/ARQUITECTURA.md §2`.

### D5: React Hook Form + Zod para validación de formularios

**Decisión**: Formularios usan `react-hook-form` con resolver `@hookform/resolvers/zod`. Schemas Zod reflejan las restricciones del backend (email válido, password mínimo 8 chars, TOTP 6 dígitos).

**Ejemplo de schema Zod para login**:
```ts
const loginSchema = z.object({
  email: z.string().email('Email inválido'),
  password: z.string().min(1, 'La contraseña es requerida'),
});
```

### D6: Tailwind CSS sin CSS modules

**Decisión**: Estilos exclusivamente con clases utilitarias de Tailwind. Sin archivos `.module.css`, sin styled-components, sin inline styles (salvo valores dinámicos donde Tailwind no alcanza).

**Racional**: Consistencia con el estándar del proyecto. Tailwind v3 con JIT.

### D7: Menú de navegación por permisos

**Decisión**: El sidebar del shell construye los items de menú a partir de un mapa estático `menuItems` que asocia cada ruta con los permisos requeridos. El componente filtra los items según los roles del JWT (que vienen en los claims). Como los permisos se resuelven server-side, el frontend solo oculta items de menú — el guard `require_permission` del backend es la verdadera barrera de seguridad.

```ts
type MenuItem = {
  label: string;
  path: string;
  icon: React.ComponentType;
  requiredRoles: string[]; // roles que ven este item
};
```

### D8: Estructura de directorios

Siguiendo `docs/ARQUITECTURA.md §4`:

```
frontend/
├── index.html
├── package.json
├── tsconfig.json
├── vite.config.ts
├── tailwind.config.js
├── postcss.config.js
└── src/
    ├── main.tsx                    # Entry point, Providers wrapper
    ├── App.tsx                     # Router setup
    ├── vite-env.d.ts
    ├── features/
    │   └── auth/
    │       ├── components/         # LoginForm, TwoFactorForm, ForgotPasswordForm, ResetPasswordForm
    │       ├── hooks/              # useLogin, useLogout, useRefresh, useForgotPassword, useResetPassword
    │       ├── services/           # authService.ts (funciones fetch wrapper)
    │       ├── types/              # auth.types.ts (LoginRequest, LoginResponse, etc.)
    │       └── pages/              # LoginPage, TwoFactorPage, ForgotPasswordPage, ResetPasswordPage
    └── shared/
        ├── services/
        │   └── api.ts              # Axios instance + interceptors
        ├── components/             # ProtectedRoute, PublicRoute, AppShell, Sidebar, Header, UnauthorizedPage
        ├── hooks/                  # useAuth, usePermissions
        ├── contexts/               # AuthContext, AuthProvider
        └── types/                  # api.types.ts, auth.types.ts (shared)
```

## Risks / Trade-offs

- **[Riesgo] Pérdida de sesión al recargar página**: Como los tokens están en memoria, un F5 fuerza re-login. **Mitigación**: En fase 2, si se vuelve crítico, se puede persistir el refresh token en una httpOnly cookie seteada por el backend (requiere cambio en C-03). Para MVP con sesiones de 15 min es aceptable.
- **[Riesgo] Race condition en refresh concurrente**: Si múltiples requests concurrentes reciben 401, todas intentarían refrescar. **Mitigación**: El interceptor usa una promise en vuelo (`refreshPromise`) — la primera request hace el refresh, las demás esperan y reusan el resultado.
- **[Riesgo] Tenant ID en variable de entorno**: `VITE_TENANT_ID` se build-timea. Si un mismo build sirve múltiples tenants, esto no funciona. **Mitigación**: En MVP con un tenant por despliegue alcanza. Si se necesita multi-tenant en mismo frontend, se deriva del subdominio (window.location.hostname).
- **[Trade-off] Sin i18n**: Las strings están hardcodeadas en español. Es aceptable para MVP con tenants hispanohablantes. Agregar i18n es trivial con react-i18next cuando se necesite.

## Open Questions

- **¿Persistir refresh token en cookie httpOnly?**: Evaluar post-MVP si el UX de perder sesión en reload es inaceptable. Requiere cambio en backend (C-03) para setear cookie en login/refresh.
- **¿Detección de tenant por subdominio vs env var?**: Si Easypanel despliega múltiples tenants con mismo build, necesitamos detección por subdominio. Definir con el equipo de infra.
