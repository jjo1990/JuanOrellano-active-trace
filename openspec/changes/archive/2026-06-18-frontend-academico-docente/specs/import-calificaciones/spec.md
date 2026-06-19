## ADDED Requirements

### Requirement: Upload de archivo de calificaciones
El sistema SHALL permitir al PROFESOR subir un archivo de calificaciones exportado del LMS (xlsx/csv) y obtener una vista previa de las actividades y alumnos detectados.

#### Scenario: Upload exitoso con preview
- **WHEN** el usuario selecciona una materia, sube un archivo .xlsx y hace clic en "Previsualizar"
- **THEN** el sistema muestra una tabla con alumnos (filas) y actividades detectadas (columnas), con checkbox por actividad.

#### Scenario: Archivo inválido
- **WHEN** el usuario sube un archivo que no es .xlsx ni .csv
- **THEN** el sistema muestra un mensaje de error "Formato no soportado. Usá .xlsx o .csv".

### Requirement: Selección de actividades a importar
El sistema SHALL permitir al usuario seleccionar qué actividades del preview incluir en la importación definitiva.

#### Scenario: Seleccionar actividades y confirmar
- **WHEN** el usuario selecciona 3 de 5 actividades detectadas y hace clic en "Importar seleccionadas"
- **THEN** el sistema envía la confirmación al backend, muestra un spinner durante la importación, y redirige al dashboard de la materia con un mensaje de éxito.

#### Scenario: No seleccionar ninguna actividad
- **WHEN** el usuario hace clic en "Importar" sin seleccionar ninguna actividad
- **THEN** el sistema muestra un error de validación "Seleccioná al menos una actividad".
