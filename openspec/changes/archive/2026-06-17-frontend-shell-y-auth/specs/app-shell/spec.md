## ADDED Requirements

### Requirement: Responsive sidebar navigation

The system SHALL render a sidebar navigation in the application shell. On desktop viewports (≥768px), the sidebar SHALL be always visible. On mobile viewports (<768px), the sidebar SHALL be collapsible via a hamburger menu toggle. The sidebar SHALL contain navigation items that lead to feature pages.

#### Scenario: Desktop layout shows sidebar
- **WHEN** the viewport is 1024px wide and user is authenticated
- **THEN** the sidebar SHALL be visible and display navigation items

#### Scenario: Mobile layout hides sidebar by default
- **WHEN** the viewport is 375px wide and user is authenticated
- **THEN** the sidebar SHALL be hidden and a hamburger button SHALL be visible in the header

#### Scenario: Mobile sidebar toggle
- **WHEN** user taps the hamburger button on mobile
- **THEN** the sidebar SHALL slide in from the left and an overlay SHALL cover the content area

### Requirement: Navigation menu by permissions

The system SHALL build the sidebar navigation menu dynamically based on the user's roles from the JWT claims. Menu items associated with roles the user does NOT have SHALL be hidden. This is a UX optimization — the backend SHALL still enforce permissions via RBAC on every endpoint.

#### Scenario: PROFESOR only sees their items
- **WHEN** a user with role PROFESOR is authenticated
- **THEN** the menu SHALL show only items available to PROFESOR (e.g., Mis comisiones, Comunicación, Perfil)

#### Scenario: ADMIN sees admin items
- **WHEN** a user with role ADMIN is authenticated
- **THEN** the menu SHALL show admin items (e.g., Estructura académica, Usuarios, Auditoría, Perfil)

#### Scenario: Empty menu for role with no items
- **WHEN** a user with a role that has no configured menu items logs in
- **THEN** the sidebar SHALL render empty of navigation items but with the user info and logout option visible

### Requirement: User info in header

The system SHALL display the authenticated user's display name (nombre + apellidos) and email in the application header. The header SHALL be visible on all protected pages inside the application shell.

#### Scenario: Header shows logged-in user info
- **WHEN** a user with nombre="María" and apellidos="González" is authenticated
- **THEN** the header SHALL display "María González" and the user's email

### Requirement: Logout button

The system SHALL render a logout button in the application header or sidebar. Clicking logout SHALL call the logout endpoint and redirect to `/login`.

#### Scenario: User clicks logout
- **WHEN** user clicks the logout button
- **THEN** the system SHALL call `POST /api/auth/logout`, clear the auth context, and redirect to `/login`

### Requirement: Content outlet

The system SHALL render the matched child route content in a main content area using React Router's `<Outlet />`. The content area SHALL be scrollable independently from the sidebar and header.

#### Scenario: Navigate to a feature page
- **WHEN** user clicks "Perfil" in the sidebar navigation
- **THEN** the content area SHALL render the Perfil page component while the sidebar and header remain visible

### Requirement: Unauthorized page

The system SHALL render an unauthorized page at `/app/unauthorized` when the user's roles do not grant access to a feature. This page SHALL display a message and a link back to the main dashboard.

#### Scenario: User without permission visits restricted route
- **WHEN** a user without the appropriate permission visits a route that returns 403 from the API
- **THEN** the system SHALL redirect to `/app/unauthorized` with a message "No tiene permisos para acceder a esta sección."

### Requirement: Dashboard landing page

The system SHALL render a dashboard/landing page at `/app` as the default route after login. In this initial version, the dashboard SHALL display a welcome message with the user's name and a brief description of the platform's purpose. Feature-specific dashboard widgets SHALL be added in C-22, C-23, C-24.

#### Scenario: User logs in and sees dashboard
- **WHEN** a user successfully authenticates
- **THEN** the system SHALL navigate to `/app` and display "Bienvenido/a, [display_name]" with a brief platform description
