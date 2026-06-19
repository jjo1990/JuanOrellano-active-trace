## ADDED Requirements

### Requirement: Wizard de setup de cuatrimestre
El sistema SHALL guiar al COORDINADOR en un flujo de 5 pasos para configurar un nuevo período académico.

#### Scenario: Flujo completo
- **WHEN** el usuario completa los 5 pasos en orden (Cohorte → Docentes → Padrón → Fechas → Confirmar)
- **THEN** el sistema persiste la configuración y muestra resumen final con indicador 5/5 completado.

#### Scenario: Guardar progreso parcial
- **WHEN** el usuario completa 3 de 5 pasos y sale
- **THEN** el sistema guarda el progreso en sessionStorage y permite retomar donde quedó.

### Requirement: Navegación entre pasos
El sistema SHALL mostrar un stepper visual con los 5 pasos, indicando completado/actual/pendiente, y permitir navegación solo hacia atrás.

#### Scenario: Ver progreso del wizard
- **WHEN** el usuario está en el paso 3
- **THEN** el stepper muestra pasos 1 y 2 como ✓ completados, paso 3 como activo, pasos 4 y 5 bloqueados.
