## ADDED Requirements

### Requirement: Materia tiene grupo de plus opcional
El sistema SHALL permitir que cada `Materia` tenga un campo `grupo_plus` (texto, nullable) que la asocia a un grupo de plus salarial. Este campo es configurable por el ADMIN del tenant mediante el endpoint de modificación de materia.

#### Scenario: Asignar grupo_plus a materia
- **WHEN** ADMIN envía `PUT /api/admin/materias/{id}` con `grupo_plus=PROG`
- **THEN** el sistema actualiza el campo y retorna 200 con la materia actualizada.

#### Scenario: Materia sin grupo_plus no genera plus
- **WHEN** una materia tiene `grupo_plus=null`, las asignaciones a esa materia no contribuyen al cálculo de plus en liquidaciones.

#### Scenario: Consultar materias por grupo_plus
- **WHEN** se solicita `GET /api/admin/materias?grupo_plus=PROG`
- **THEN** el sistema retorna solo las materias del tenant con ese grupo_plus.
