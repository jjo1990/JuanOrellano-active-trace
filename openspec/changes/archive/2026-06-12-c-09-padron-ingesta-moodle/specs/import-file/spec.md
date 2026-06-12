## ADDED Requirements

### Requirement: Importar padrón desde archivo XLSX/CSV

El sistema SHALL permitir importar el padrón de alumnos desde archivos `.xlsx` (via openpyxl) y `.csv` (via csv module). El flujo SHALL ser: upload → parse → preview (retorna token efímero) → confirm → persist. El upsert SHALL ser destructivo (RN-05): la confirmación reemplaza completamente el padrón anterior de la materia.

#### Scenario: Upload de archivo XLSX válido

- **GIVEN** un archivo .xlsx con columnas nombre, apellidos, email, comision, regional
- **WHEN** se envía el archivo al endpoint `POST /api/padron/import`
- **THEN** el sistema parsea el archivo y retorna un `preview_token` con resumen de filas detectadas
- **AND** retorna las primeras N filas como vista previa

#### Scenario: Upload de archivo CSV válido

- **GIVEN** un archivo .csv (delimitado por coma o punto y coma) con las mismas columnas
- **WHEN** se envía al endpoint `POST /api/padron/import`
- **THEN** se parsea correctamente distinguiendo separador por sniffing
- **AND** retorna preview token

#### Scenario: Confirmar importación con preview_token

- **GIVEN** un preview_token válido obtenido del paso anterior
- **WHEN** se llama a `POST /api/padron/confirm/<token>`
- **THEN** se crea una nueva `VersionPadron` activa
- **AND** se desactiva la versión anterior para esa (materia, cohorte)
- **AND** se persisten todas las `EntradaPadron` parseadas
- **AND** se registra un audit log con acción `PADRON_CARGAR`

#### Scenario: Archivo con columnas faltantes

- **GIVEN** un archivo que no contiene las columnas requeridas (nombre, apellidos, email)
- **WHEN** se envía al endpoint de import
- **THEN** el sistema retorna error 422 con detalle de columnas faltantes

#### Scenario: Preview token expirado o inválido

- **GIVEN** un preview_token inválido o expirado
- **WHEN** se intenta confirmar la importación
- **THEN** el sistema retorna error 404 (token no encontrado o expirado)

#### Scenario: Permiso padron:importar requerido

- **GIVEN** un usuario sin permiso `padron:importar`
- **WHEN** intenta acceder al endpoint de import
- **THEN** el sistema retorna 403 Forbidden
