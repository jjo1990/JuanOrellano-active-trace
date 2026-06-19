# auth-screen Specification

## Purpose
TBD - created by archiving change frontend-shell-y-auth. Update Purpose after archive.
## Requirements
### Requirement: Login screen

The system SHALL render a login form with email and password fields. On successful authentication, the user SHALL be redirected to the application shell. If the user's account has 2FA enabled, the system SHALL redirect to the 2FA challenge screen with the challenge token received from the backend.

#### Scenario: Successful login without 2FA
- **WHEN** user submits valid email and password for an account without 2FA
- **THEN** the system stores access_token and refresh_token in AuthContext and navigates to `/app`

#### Scenario: Successful login with 2FA required
- **WHEN** user submits valid email and password for an account with 2FA enabled
- **THEN** the system navigates to the 2FA challenge screen and passes the challenge_token

#### Scenario: Invalid credentials
- **WHEN** user submits invalid email or password
- **THEN** the system displays an error message ("Credenciales inválidas") and does NOT redirect

#### Scenario: Empty form submission
- **WHEN** user submits the form with empty email or password
- **THEN** the system SHALL display inline validation errors and NOT call the backend

#### Scenario: Network error during login
- **WHEN** the login request fails with a network error
- **THEN** the system SHALL display a generic error message ("Error de conexión. Intente nuevamente.")

### Requirement: Two-factor authentication challenge

The system SHALL render a TOTP code input screen when login returns `requires_2fa: true`. The screen SHALL accept a 6-digit numeric code. On successful verification, the user SHALL be redirected to the application shell.

#### Scenario: Valid TOTP code
- **WHEN** user enters a valid TOTP code and submits
- **THEN** the system stores access_token and refresh_token in AuthContext and navigates to `/app`

#### Scenario: Invalid TOTP code
- **WHEN** user enters an invalid TOTP code
- **THEN** the system SHALL display an error message ("Código inválido") and keep the user on the 2FA screen

#### Scenario: Expired challenge token
- **WHEN** the challenge_token has expired and user submits TOTP code
- **THEN** the system SHALL display an error message and redirect the user back to the login screen

#### Scenario: Non-numeric TOTP input
- **WHEN** user enters a non-numeric value in the TOTP field
- **THEN** the system SHALL display a validation error ("El código debe ser numérico")

### Requirement: Forgot password flow

The system SHALL provide a forgot password screen where users enter their email. On submission, the system SHALL display a confirmation message regardless of whether the email exists (to prevent email enumeration). The confirmation message SHALL instruct the user to check their inbox.

#### Scenario: Email submitted successfully
- **WHEN** user submits a valid email format on the forgot password screen
- **THEN** the system SHALL call `POST /api/auth/forgot` and display "Si el email está registrado, recibirás un enlace para recuperar tu contraseña."

#### Scenario: Invalid email format
- **WHEN** user submits an invalid email format
- **THEN** the system SHALL display an inline validation error and NOT call the backend

### Requirement: Reset password screen

The system SHALL render a reset password screen accessible via a link containing a one-time token (as query parameter `?token=...`). The screen SHALL have fields for new password and confirmation. On successful reset, the system SHALL display a success message with a link to the login screen.

#### Scenario: Successful password reset
- **WHEN** user submits a valid token, new password (min 8 chars), and matching confirmation
- **THEN** the system SHALL call `POST /api/auth/reset` and display "Contraseña actualizada correctamente." with a link to login

#### Scenario: Passwords do not match
- **WHEN** user submits a valid token but new password and confirmation do not match
- **THEN** the system SHALL display "Las contraseñas no coinciden." and NOT call the backend

#### Scenario: Password too short
- **WHEN** user submits a valid token but a password shorter than 8 characters
- **THEN** the system SHALL display "La contraseña debe tener al menos 8 caracteres." and NOT call the backend

#### Scenario: Invalid or expired token
- **WHEN** user submits an invalid or expired reset token
- **THEN** the system SHALL display an error message and a link to request a new reset

### Requirement: Logout

The system SHALL provide a logout action in the application shell. On logout, the system SHALL call `POST /api/auth/logout` with the current refresh token, clear the session from AuthContext, and redirect to the login screen.

#### Scenario: Successful logout
- **WHEN** user clicks the logout button
- **THEN** the system SHALL call the logout endpoint, clear auth state, and redirect to `/login`

#### Scenario: Logout with network error
- **WHEN** the logout request fails with a network error
- **THEN** the system SHALL still clear auth state locally and redirect to `/login` (the session is terminated client-side regardless)

### Requirement: Session persistence during navigation

The system SHALL maintain the authenticated session across navigation within the protected routes. The AuthContext SHALL be accessible from any component inside the AuthProvider.

#### Scenario: Navigate between protected pages
- **WHEN** an authenticated user navigates between pages within the app shell
- **THEN** the session SHALL remain active and the access_token SHALL be available for all API calls

