## ADDED Requirements

### Requirement: Public route guard

The system SHALL provide a guard component for public routes (login, forgot password, reset password). When a user with an active session navigates to a public route, the guard SHALL redirect to `/app`. When a user without a session navigates to a public route, the guard SHALL render the route normally.

#### Scenario: Authenticated user visits login page
- **WHEN** an authenticated user navigates to `/login`
- **THEN** the system SHALL redirect to `/app`

#### Scenario: Unauthenticated user visits login page
- **WHEN** an unauthenticated user navigates to `/login`
- **THEN** the system SHALL render the login page

#### Scenario: Authenticated user visits forgot password page
- **WHEN** an authenticated user navigates to `/forgot-password`
- **THEN** the system SHALL redirect to `/app`

### Requirement: Protected route guard

The system SHALL provide a guard component for protected routes (app shell and all features). When a user without a session navigates to a protected route, the guard SHALL redirect to `/login`. When a user with an active session navigates to a protected route, the guard SHALL render the route normally.

#### Scenario: Unauthenticated user visits protected route
- **WHEN** an unauthenticated user navigates to `/app`
- **THEN** the system SHALL redirect to `/login`

#### Scenario: Authenticated user visits protected route
- **WHEN** an authenticated user navigates to `/app`
- **THEN** the system SHALL render the application shell

#### Scenario: Unauthenticated user visits a nested protected route
- **WHEN** an unauthenticated user navigates to `/app/perfil`
- **THEN** the system SHALL redirect to `/login`

### Requirement: Fallback route

The system SHALL redirect unknown routes to `/login`. Routes that match no defined path pattern SHALL not render a blank page or produce a 404 error visible to the user.

#### Scenario: User navigates to an unknown path
- **WHEN** a user navigates to `/nonexistent`
- **THEN** the system SHALL redirect to `/login`

### Requirement: Auth state initialization

The system SHALL initialize the auth state on application startup. If no valid session exists, the system SHALL render the public routes. The initialization SHALL complete before rendering protected routes to prevent flash-of-content on protected pages.

#### Scenario: App loads with no stored session
- **WHEN** the application initializes with no tokens in memory
- **THEN** the auth state SHALL be `{isAuthenticated: false, isLoading: false}` and protected routes SHALL redirect to `/login`

#### Scenario: App loads and determines auth state
- **WHEN** the application is initializing auth state
- **THEN** the auth provider SHALL set `isLoading: true` during initialization and protected routes SHALL show a loading indicator until initialization completes
