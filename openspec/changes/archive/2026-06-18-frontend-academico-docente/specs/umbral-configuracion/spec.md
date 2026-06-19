## ADDED Requirements

### Requirement: Configurar umbral de aprobación
El sistema SHALL permitir al PROFESOR configurar el porcentaje mínimo de nota considerada aprobatoria para su materia, con valor por defecto 60%.

#### Scenario: Configurar umbral
- **WHEN** el usuario accede a la página de umbral de una materia, ingresa "70" y guarda
- **THEN** el sistema persiste el umbral y muestra confirmación "Umbral actualizado a 70%".

#### Scenario: Valor por defecto
- **WHEN** el usuario accede por primera vez a la página de umbral de una materia sin umbral configurado
- **THEN** el sistema muestra "60%" como valor inicial.

#### Scenario: Valor fuera de rango
- **WHEN** el usuario ingresa "150" o "-5" como umbral
- **THEN** el sistema muestra error de validación "El umbral debe estar entre 0 y 100".
