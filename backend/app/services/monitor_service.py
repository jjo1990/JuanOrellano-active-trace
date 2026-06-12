import uuid
from collections.abc import Sequence

from app.models.calificacion import Calificacion
from app.models.entrada_padron import EntradaPadron
from app.services.analisis_service import AnalisisService


class MonitorService(AnalisisService):
    def _resolve_estado(
        self,
        cals: list[Calificacion],
        universo: set[str],
        umbral_pct: int,
        valores_aprobatorios: Sequence[str],
    ) -> str:
        if not universo:
            return "sin_datos"
        actividades_presentes = {c.actividad for c in cals}
        faltantes = universo - actividades_presentes
        tiene_baja = any(
            not self._es_aprobado(c, umbral_pct, valores_aprobatorios)
            for c in cals
        )
        if faltantes or tiene_baja:
            if actividades_presentes == universo and not faltantes:
                return "atrasado"
            return "atrasado"
        if actividades_presentes == universo and not tiene_baja:
            return "aprobado_todos"
        return "al_dia"

    async def get_monitor(
        self,
        materia_id: uuid.UUID | None = None,
        regional: str | None = None,
        comision: str | None = None,
        alumno: str | None = None,
        estado: str | None = None,
    ) -> "MonitorResponse":
        from app.schemas.analisis import MonitorEntryDTO, MonitorResponse

        if materia_id is not None:
            materias_ids = [materia_id]
        else:
            all_entradas = await self._get_all_entradas_activas()
            materias_ids = list({e.version.materia_id for e in all_entradas if e.version})

        estudiantes: list[MonitorEntryDTO] = []

        for mid in materias_ids:
            entradas = await self._get_entradas_activas(mid)
            universo = await self._get_actividades_universo(mid)
            umbral = await self._get_umbral(mid)
            cal_agrupadas = await self._get_calificaciones_agrupadas(mid)

            materia_nombre = await self._get_materia_nombre(mid)

            for entrada in entradas:
                if regional and entrada.regional != regional:
                    continue
                if comision and entrada.comision != comision:
                    continue
                if alumno and alumno.lower() not in entrada.nombre.lower() and alumno.lower() not in entrada.apellidos.lower():
                    continue

                cals = cal_agrupadas.get(entrada.id, [])
                resolved_estado = self._resolve_estado(cals, universo, umbral["umbral_pct"], umbral["valores_aprobatorios"])

                if estado and resolved_estado != estado:
                    continue

                aprobadas = sum(
                    1 for c in cals
                    if self._es_aprobado(c, umbral["umbral_pct"], umbral["valores_aprobatorios"])
                )
                faltantes = len(universo) - len({c.actividad for c in cals})

                ultima = None
                if cals:
                    cals_ordenadas = sorted(cals, key=lambda c: c.importado_at, reverse=True)
                    ultima = cals_ordenadas[0].actividad

                estudiantes.append(MonitorEntryDTO(
                    entrada_padron_id=entrada.id,
                    nombre=entrada.nombre,
                    apellidos=entrada.apellidos,
                    email=entrada.email or "",
                    materia_id=mid,
                    materia_nombre=materia_nombre,
                    comision=entrada.comision,
                    regional=entrada.regional,
                    estado=resolved_estado,
                    total_actividades=len(universo),
                    aprobadas=aprobadas,
                    faltantes=faltantes,
                    ultima_actividad=ultima,
                ))

        return MonitorResponse(total=len(estudiantes), estudiantes=estudiantes)

    async def get_monitor_seguimiento(
        self,
        user_id: uuid.UUID,
        alumno: str | None = None,
        comision: str | None = None,
        regional: str | None = None,
        actividad: str | None = None,
        min_aprobadas: int | None = None,
    ) -> "SeguimientoResponse":
        from app.repositories.asignacion_repository import AsignacionRepository
        from app.schemas.analisis import SeguimientoEntryDTO, SeguimientoResponse

        asign_repo = AsignacionRepository(self._session, self._tenant_id)
        asignaciones = await asign_repo.list_by_usuario(user_id)
        materias_ids = list({a.materia_id for a in asignaciones if a.materia_id})

        estudiantes: list[SeguimientoEntryDTO] = []

        for mid in materias_ids:
            entradas = await self._get_entradas_activas(mid)
            universo = await self._get_actividades_universo(mid)
            umbral = await self._get_umbral(mid)
            cal_agrupadas = await self._get_calificaciones_agrupadas(mid)

            materia_nombre = await self._get_materia_nombre(mid)

            for entrada in entradas:
                if comision and entrada.comision != comision:
                    continue
                if regional and entrada.regional != regional:
                    continue
                if alumno and alumno.lower() not in entrada.nombre.lower() and alumno.lower() not in entrada.apellidos.lower():
                    continue

                cals = cal_agrupadas.get(entrada.id, [])
                resolved_estado = self._resolve_estado(cals, universo, umbral["umbral_pct"], umbral["valores_aprobatorios"])

                aprobadas = sum(
                    1 for c in cals
                    if self._es_aprobado(c, umbral["umbral_pct"], umbral["valores_aprobatorios"])
                )

                if min_aprobadas is not None and aprobadas < min_aprobadas:
                    continue

                if actividad is not None:
                    cals_filtradas = [c for c in cals if c.actividad == actividad]
                    faltantes = 1 if not cals_filtradas else 0
                else:
                    faltantes = len(universo) - len({c.actividad for c in cals})

                estudiantes.append(SeguimientoEntryDTO(
                    entrada_padron_id=entrada.id,
                    nombre=entrada.nombre,
                    apellidos=entrada.apellidos,
                    email=entrada.email or "",
                    materia_id=mid,
                    materia_nombre=materia_nombre,
                    comision=entrada.comision,
                    regional=entrada.regional,
                    estado=resolved_estado,
                    total_actividades=len(universo),
                    aprobadas=aprobadas,
                    faltantes=faltantes,
                ))

        return SeguimientoResponse(total=len(estudiantes), estudiantes=estudiantes)

    async def get_monitor_admin(
        self,
        materia_id: uuid.UUID | None = None,
        regional: str | None = None,
        comision: str | None = None,
        alumno: str | None = None,
        estado: str | None = None,
        fecha_desde: "date | None" = None,
        fecha_hasta: "date | None" = None,
    ) -> "AdminMonitorResponse":
        from datetime import datetime, timezone
        from app.schemas.analisis import AdminMonitorEntryDTO, AdminMonitorResponse, RangoFechasDTO

        if materia_id is not None:
            materias_ids = [materia_id]
        else:
            entradas = await self._get_all_entradas_activas()
            materias_ids = list({e.version.materia_id for e in entradas if e.version})

        estudiantes: list[AdminMonitorEntryDTO] = []

        for mid in materias_ids:
            entradas = await self._get_entradas_activas(mid)
            universo = await self._get_actividades_universo(mid)
            umbral = await self._get_umbral(mid)
            cal_agrupadas = await self._get_calificaciones_agrupadas(mid)

            materia_nombre = await self._get_materia_nombre(mid)

            for entrada in entradas:
                if regional and entrada.regional != regional:
                    continue
                if comision and entrada.comision != comision:
                    continue
                if alumno and alumno.lower() not in entrada.nombre.lower() and alumno.lower() not in entrada.apellidos.lower():
                    continue

                cals = cal_agrupadas.get(entrada.id, [])
                if fecha_desde is not None:
                    desde_dt = datetime.combine(fecha_desde, datetime.min.time(), tzinfo=timezone.utc)
                    cals = [c for c in cals if c.importado_at >= desde_dt]
                if fecha_hasta is not None:
                    hasta_dt = datetime.combine(fecha_hasta, datetime.max.time(), tzinfo=timezone.utc)
                    cals = [c for c in cals if c.importado_at <= hasta_dt]

                resolved_estado = self._resolve_estado(cals, universo, umbral["umbral_pct"], umbral["valores_aprobatorios"])

                if estado and resolved_estado != estado:
                    continue

                aprobadas = sum(
                    1 for c in cals
                    if self._es_aprobado(c, umbral["umbral_pct"], umbral["valores_aprobatorios"])
                )
                faltantes = len(universo) - len({c.actividad for c in cals})

                estudiantes.append(AdminMonitorEntryDTO(
                    entrada_padron_id=entrada.id,
                    nombre=entrada.nombre,
                    apellidos=entrada.apellidos,
                    email=entrada.email or "",
                    materia_id=mid,
                    materia_nombre=materia_nombre,
                    comision=entrada.comision,
                    regional=entrada.regional,
                    estado=resolved_estado,
                    total_actividades=len(universo),
                    aprobadas=aprobadas,
                    faltantes=faltantes,
                ))

        rango = None
        if fecha_desde is not None or fecha_hasta is not None:
            rango = RangoFechasDTO(desde=fecha_desde, hasta=fecha_hasta)

        return AdminMonitorResponse(
            total=len(estudiantes),
            rango_fechas=rango,
            estudiantes=estudiantes,
        )

    async def _get_all_entradas_activas(self) -> Sequence[EntradaPadron]:
        from sqlalchemy import select
        from app.models.entrada_padron import EntradaPadron
        from app.models.version_padron import VersionPadron

        stmt = (
            select(EntradaPadron)
            .join(VersionPadron, VersionPadron.id == EntradaPadron.version_id)
            .where(
                VersionPadron.activa.is_(True),
                EntradaPadron.tenant_id == self._tenant_id,
                EntradaPadron.deleted_at.is_(None),
                VersionPadron.deleted_at.is_(None),
            )
        )
        result = await self._session.execute(stmt)
        return result.scalars().all()

    async def _get_materia_nombre(self, materia_id: uuid.UUID) -> str:
        from sqlalchemy import select
        from app.models.materia import Materia
        stmt = select(Materia.nombre).where(
            Materia.id == materia_id,
            Materia.tenant_id == self._tenant_id,
            Materia.deleted_at.is_(None),
        )
        result = await self._session.execute(stmt)
        nombre = result.scalar_one_or_none()
        return nombre or "Desconocida"
