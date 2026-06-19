## ADDED Requirements

### Requirement: Panel de auditoría con sub-vistas
El sistema SHALL mostrar un panel de auditoría con 4 sub-vistas: Acciones por día, Estado de comunicaciones, Interacciones por docente y materia, y Registro de últimas acciones. Una barra de filtros superior (rango de fechas, materia, usuario, estado de actividad) aplica a todas las sub-vistas.

#### Scenario: Ver acciones por día
- **WHEN** el usuario selecciona la sub-vista "Acciones por día"
- **THEN** el sistema muestra un gráfico de barras simple (CSS) con el volumen de acciones por día en el rango de fechas seleccionado.

#### Scenario: Ver estado de comunicaciones
- **WHEN** el usuario selecciona la sub-vista "Comunicaciones"
- **THEN** el sistema muestra una tabla con distribución de estados (Pendiente/Enviando/OK/Fallido/Cancelado) por docente y materia.

#### Scenario: Ver interacciones por docente
- **WHEN** el usuario selecciona la sub-vista "Interacciones"
- **THEN** el sistema muestra una tabla con métricas por docente y materia: análisis de desempeño, vista previa, importación, envío, limpieza de datos, configuración de umbral, emails generados, lotes procesados.

#### Scenario: Filtrar panel por rango de fechas
- **WHEN** el usuario selecciona un rango de fechas en la barra de filtros
- **THEN** todas las sub-vistas se actualizan para reflejar solo datos dentro del rango seleccionado.

### Requirement: Log de últimas acciones
El sistema SHALL mostrar los últimos registros de auditoría (máximo configurable, por defecto 200) con columnas: fecha/hora, usuario, materia, tipo de acción, registros afectados, IP, user agent.

#### Scenario: Ver últimas acciones
- **WHEN** el usuario selecciona la sub-vista "Últimas acciones"
- **THEN** el sistema muestra una tabla con los 200 registros más recientes del log de auditoría, ordenados por fecha descendente.

#### Scenario: Filtrar log por usuario
- **WHEN** el usuario selecciona un usuario específico en el filtro
- **THEN** el sistema muestra solo las acciones realizadas por ese usuario en el log de últimas acciones.
