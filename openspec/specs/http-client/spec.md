# http-client Specification

## Purpose
TBD - created by archiving change frontend-shell-y-auth. Update Purpose after archive.
## Requirements
### Requirement: Centralized Axios instance

The system SHALL provide a centralized Axios instance configured with `baseURL` from the `VITE_API_URL` environment variable (default: `http://localhost:8000`). All API requests SHALL use this instance. The instance SHALL attach the `X-Tenant-Id` header to every request, sourced from `VITE_TENANT_ID` environment variable.

#### Scenario: API request includes tenant header
- **WHEN** any API request is made through the centralized client
- **THEN** the request SHALL include the header `X-Tenant-Id` with the configured tenant ID

#### Scenario: API request uses configured base URL
- **WHEN** a request is made to `/api/health`
- **THEN** the full URL resolved SHALL be `<baseURL>/api/health`

### Requirement: JWT access token injection

The system SHALL automatically attach the `Authorization: Bearer <access_token>` header to every outgoing request when a valid access token exists in the AuthContext. Requests without a stored token SHALL NOT include the Authorization header.

#### Scenario: Request with valid token
- **WHEN** a request is made and AuthContext has a valid access_token
- **THEN** the request SHALL include the header `Authorization: Bearer <token>`

#### Scenario: Request without token (public endpoint)
- **WHEN** a request is made to a public endpoint (e.g., login) and no token is stored
- **THEN** the request SHALL NOT include the Authorization header

### Requirement: Transparent token refresh on 401

The system SHALL intercept 401 responses and attempt a transparent token refresh using the stored refresh token. If the refresh succeeds, the original request SHALL be retried with the new access token. If the refresh fails, the session SHALL be cleared and the user SHALL be redirected to `/login`.

#### Scenario: Single request gets 401 and refresh succeeds
- **WHEN** an API request returns 401 and a valid refresh_token exists
- **THEN** the interceptor SHALL call `POST /api/auth/refresh`, store the new tokens, and retry the original request with the new access_token

#### Scenario: Refresh token is invalid or expired
- **WHEN** an API request returns 401 and the refresh request also fails (returns 401)
- **THEN** the system SHALL clear the AuthContext, remove stored tokens, and redirect to `/login`

#### Scenario: Multiple concurrent requests get 401
- **WHEN** three API requests return 401 simultaneously and a refresh is already in progress
- **THEN** only one refresh request SHALL be made; the other two requests SHALL wait for the refresh to complete and retry with the new token

#### Scenario: Request returns 401 with no refresh token stored
- **WHEN** an API request returns 401 and no refresh_token exists in AuthContext (e.g., initial state)
- **THEN** the system SHALL redirect to `/login` without attempting refresh

### Requirement: 403 error handling

The system SHALL intercept 403 responses and redirect the user to `/app/unauthorized`. The unauthorized page SHALL display a message indicating the user lacks the required permissions.

#### Scenario: Authenticated user accesses a forbidden endpoint
- **WHEN** an API request returns 403 for an authenticated user
- **THEN** the system SHALL navigate to `/app/unauthorized` and display an appropriate message

### Requirement: Generic network error handling

The system SHALL handle network errors (no response from server, timeout) by displaying a user-friendly error toast or message. Network errors SHALL NOT cause the application to crash or enter an unrecoverable state.

#### Scenario: Backend is unreachable
- **WHEN** an API request fails with a network error (no response)
- **THEN** the system SHALL display an error toast: "Error de conexión. Verifique su conexión a internet."

#### Scenario: Request timeout
- **WHEN** an API request exceeds the configured timeout (15 seconds)
- **THEN** the system SHALL display an error toast and allow the user to retry

### Requirement: Token storage in memory only

The system SHALL store access and refresh tokens exclusively in React Context (memory). Tokens SHALL NOT be persisted to localStorage, sessionStorage, or cookies from the frontend side.

#### Scenario: Page reload clears session
- **WHEN** the user reloads the browser page
- **THEN** the tokens in memory are lost and the user must re-authenticate

