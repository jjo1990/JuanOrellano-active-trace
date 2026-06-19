## ADDED Requirements

### Requirement: ABM de avisos
El sistema SHALL permitir al COORDINADOR crear, editar y eliminar avisos con configuración de scope, severidad y vigencia.

#### Scenario: Crear aviso global
- **WHEN** el usuario crea un aviso con scope "Global", severidad "Alta", vigencia desde/hasta, y guarda
- **THEN** el sistema crea el aviso y lo muestra en la lista.

#### Scenario: Crear aviso por materia
- **WHEN** el usuario crea un aviso con scope "PorMateria", selecciona una materia específica y un rol destino
- **THEN** el sistema asocia el aviso a esa materia, visible solo para usuarios con ese rol en esa materia.

### Requirement: Vista de acknowledgments
El sistema SHALL mostrar qué usuarios confirmaron la lectura de un aviso que requiere ack.

#### Scenario: Ver confirmaciones
- **WHEN** el usuario abre el detalle de un aviso con `requiere_ack=true`
- **THEN** el sistema muestra lista de usuarios que confirmaron y los pendientes, con contadores.
