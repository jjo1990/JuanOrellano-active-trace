import logging
import uuid
from collections.abc import Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.calificacion import Calificacion
from app.models.entrada_padron import EntradaPadron
from app.models.umbral_materia import UmbralMateria
from app.repositories.calificaciones_repository import CalificacionesRepository
from app.repositories.padron_repository import PadronRepository

logger = logging.getLogger(__name__)

_DEFAULT_UMBRAL_PCT = 60
_DEFAULT_VALORES_APROBATORIOS = ("Satisfactorio", "Supera lo esperado")


class AnalisisService:
    def __init__(self, session: AsyncSession, tenant_id: uuid.UUID) -> None:
        self._cal_repo = CalificacionesRepository(session, tenant_id)
        self._padron_repo = PadronRepository(session, tenant_id)
        self._session = session
        self._tenant_id = tenant_id

    @staticmethod
    def _es_aprobado(
        cal: Calificacion,
        umbral_pct: int = _DEFAULT_UMBRAL_PCT,
        valores_aprobatorios: Sequence[str] = _DEFAULT_VALORES_APROBATORIOS,
    ) -> bool:
        if cal.nota_numerica is not None:
            return cal.nota_numerica >= umbral_pct
        if cal.nota_textual is not None:
            return cal.nota_textual in valores_aprobatorios
        return False

    async def _get_umbral(self, materia_id: uuid.UUID) -> dict:
        umbral = await self._cal_repo.get_umbral_by_materia(materia_id)
        if umbral is not None:
            return {
                "umbral_pct": umbral.umbral_pct,
                "valores_aprobatorios": tuple(umbral.valores_aprobatorios),
            }
        return {
            "umbral_pct": _DEFAULT_UMBRAL_PCT,
            "valores_aprobatorios": _DEFAULT_VALORES_APROBATORIOS,
        }

    async def _get_actividades_universo(self, materia_id: uuid.UUID) -> set[str]:
        calificaciones = await self._cal_repo.get_calificaciones_by_materia(materia_id)
        return {c.actividad for c in calificaciones}

    async def _get_entradas_activas(self, materia_id: uuid.UUID) -> Sequence[EntradaPadron]:
        return await self._padron_repo.get_entradas_activas_por_materia(materia_id)

    async def _get_calificaciones_agrupadas(
        self, materia_id: uuid.UUID,
    ) -> dict[uuid.UUID, list[Calificacion]]:
        calificaciones = await self._cal_repo.get_calificaciones_by_materia(materia_id)
        agrupadas: dict[uuid.UUID, list[Calificacion]] = {}
        for cal in calificaciones:
            agrupadas.setdefault(cal.entrada_padron_id, []).append(cal)
        return agrupadas

    async def get_atrasados(self, materia_id: uuid.UUID) -> "AtrasadosResponse":
        from app.schemas.analisis import AlumnoAtrasadoDTO, AtrasadosResponse, NotaBajaDTO

        entradas = await self._get_entradas_activas(materia_id)
        universo = await self._get_actividades_universo(materia_id)
        umbral = await self._get_umbral(materia_id)
        cal_agrupadas = await self._get_calificaciones_agrupadas(materia_id)

        if not universo:
            return AtrasadosResponse(
                materia_id=materia_id,
                total_alumnos=len(entradas),
                total_atrasados=0,
                atrasados=[],
                status_info="Sin datos de calificaciones para esta materia",
            )

        atrasados: list[AlumnoAtrasadoDTO] = []
        for entrada in entradas:
            cals = cal_agrupadas.get(entrada.id, [])
            actividades_presentes = {c.actividad for c in cals}
            actividades_faltantes = sorted(universo - actividades_presentes)

            notas_bajas: list[NotaBajaDTO] = []
            for c in cals:
                if not self._es_aprobado(c, umbral["umbral_pct"], umbral["valores_aprobatorios"]):
                    notas_bajas.append(NotaBajaDTO(
                        actividad=c.actividad,
                        nota=c.nota_numerica,
                        nota_textual=c.nota_textual,
                    ))

            if actividades_faltantes or notas_bajas:
                atrasados.append(AlumnoAtrasadoDTO(
                    entrada_padron_id=entrada.id,
                    nombre=entrada.nombre,
                    apellidos=entrada.apellidos,
                    email=entrada.email or "",
                    comision=entrada.comision,
                    regional=entrada.regional,
                    actividades_faltantes=actividades_faltantes,
                    notas_bajas=notas_bajas,
                ))

        return AtrasadosResponse(
            materia_id=materia_id,
            total_alumnos=len(entradas),
            total_atrasados=len(atrasados),
            atrasados=atrasados,
            status_info=None,
        )

    async def get_ranking(self, materia_id: uuid.UUID) -> "RankingResponse":
        from app.schemas.analisis import RankingEntryDTO, RankingResponse

        entradas = await self._get_entradas_activas(materia_id)
        universo = await self._get_actividades_universo(materia_id)
        umbral = await self._get_umbral(materia_id)
        cal_agrupadas = await self._get_calificaciones_agrupadas(materia_id)

        if not universo:
            return RankingResponse(
                materia_id=materia_id,
                total_alumnos=len(entradas),
                ranking=[],
                status_info="Sin datos de calificaciones para esta materia",
            )

        total_actividades = len(universo)
        ranking: list[RankingEntryDTO] = []

        for entrada in entradas:
            cals = cal_agrupadas.get(entrada.id, [])
            aprobadas = sum(
                1 for c in cals
                if self._es_aprobado(c, umbral["umbral_pct"], umbral["valores_aprobatorios"])
            )
            if aprobadas == 0:
                continue
            porcentaje = round((aprobadas / total_actividades) * 100, 2)
            ranking.append(RankingEntryDTO(
                entrada_padron_id=entrada.id,
                nombre=entrada.nombre,
                apellidos=entrada.apellidos,
                email=entrada.email or "",
                comision=entrada.comision,
                regional=entrada.regional,
                total_actividades=total_actividades,
                aprobadas=aprobadas,
                porcentaje=porcentaje,
            ))

        ranking.sort(key=lambda x: x.aprobadas, reverse=True)

        status_info = None
        if not ranking:
            status_info = "Ningun alumno tiene actividades aprobadas"

        return RankingResponse(
            materia_id=materia_id,
            total_alumnos=len(entradas),
            ranking=ranking,
            status_info=status_info,
        )

    async def get_reportes(self, materia_id: uuid.UUID) -> "ReportesResponse":
        from app.schemas.analisis import ReportesResponse

        entradas = await self._get_entradas_activas(materia_id)
        universo = await self._get_actividades_universo(materia_id)
        umbral = await self._get_umbral(materia_id)
        cal_agrupadas = await self._get_calificaciones_agrupadas(materia_id)

        if not universo:
            return ReportesResponse(
                materia_id=materia_id,
                total_alumnos=len(entradas),
                total_actividades=0,
                aprobacion_general=0.0,
                distribucion_notas={},
                alumnos_al_dia=0,
                alumnos_atrasados=0,
                status_info="Sin datos de calificaciones para esta materia",
            )

        todas_cals = [c for cals in cal_agrupadas.values() for c in cals]
        total = len(todas_cals)
        aprobadas_count = sum(
            1 for c in todas_cals
            if self._es_aprobado(c, umbral["umbral_pct"], umbral["valores_aprobatorios"])
        )
        aprobacion_general = round((aprobadas_count / total) * 100, 2) if total > 0 else 0.0

        distribucion: dict[str, int] = {"0-59": 0, "60-69": 0, "70-79": 0, "80-89": 0, "90-100": 0}
        for c in todas_cals:
            if c.nota_numerica is not None:
                n = c.nota_numerica
                if n < 60:
                    distribucion["0-59"] += 1
                elif n < 70:
                    distribucion["60-69"] += 1
                elif n < 80:
                    distribucion["70-79"] += 1
                elif n < 90:
                    distribucion["80-89"] += 1
                else:
                    distribucion["90-100"] += 1

        actividad_aprobacion: dict[str, list[bool]] = {}
        for c in todas_cals:
            actividad_aprobacion.setdefault(c.actividad, []).append(
                self._es_aprobado(c, umbral["umbral_pct"], umbral["valores_aprobatorios"])
            )

        actividad_mas_dificil = None
        actividad_mas_facil = None
        if actividad_aprobacion:
            tasas = {
                act: sum(aprs) / len(aprs)
                for act, aprs in actividad_aprobacion.items()
            }
            actividad_mas_dificil = min(tasas, key=tasas.get)
            actividad_mas_facil = max(tasas, key=tasas.get)

        alumnos_al_dia = 0
        alumnos_atrasados = 0
        for entrada in entradas:
            cals = cal_agrupadas.get(entrada.id, [])
            actividades_presentes = {c.actividad for c in cals}
            faltantes = universo - actividades_presentes
            tiene_baja = any(
                not self._es_aprobado(c, umbral["umbral_pct"], umbral["valores_aprobatorios"])
                for c in cals
            )
            if faltantes or tiene_baja:
                alumnos_atrasados += 1
            else:
                alumnos_al_dia += 1

        return ReportesResponse(
            materia_id=materia_id,
            total_alumnos=len(entradas),
            total_actividades=len(universo),
            aprobacion_general=aprobacion_general,
            distribucion_notas={k: v for k, v in distribucion.items() if v > 0},
            alumnos_al_dia=alumnos_al_dia,
            alumnos_atrasados=alumnos_atrasados,
            actividad_mas_dificil=actividad_mas_dificil,
            actividad_mas_facil=actividad_mas_facil,
        )

    async def get_notas_finales(self, materia_id: uuid.UUID) -> "NotasFinalesResponse":
        from app.schemas.analisis import CalificacionItemDTO, NotaFinalDTO, NotasFinalesResponse

        entradas = await self._get_entradas_activas(materia_id)
        universo = await self._get_actividades_universo(materia_id)
        umbral = await self._get_umbral(materia_id)
        cal_agrupadas = await self._get_calificaciones_agrupadas(materia_id)

        if not universo:
            return NotasFinalesResponse(
                materia_id=materia_id,
                notas=[],
                status_info="Sin datos de calificaciones para esta materia",
            )

        entradas_map = {e.id: e for e in entradas}
        notas: list[NotaFinalDTO] = []

        for entrada_id, cals in cal_agrupadas.items():
            entrada = entradas_map.get(entrada_id)
            if entrada is None:
                continue

            cal_items: list[CalificacionItemDTO] = []
            numericas: list[float] = []
            todas_aprobadas = True

            for c in cals:
                aprobado = self._es_aprobado(c, umbral["umbral_pct"], umbral["valores_aprobatorios"])
                if not aprobado:
                    todas_aprobadas = False
                cal_items.append(CalificacionItemDTO(
                    id=c.id,
                    actividad=c.actividad,
                    nota_numerica=c.nota_numerica,
                    nota_textual=c.nota_textual,
                    aprobado=aprobado,
                ))
                if c.nota_numerica is not None:
                    numericas.append(c.nota_numerica)

            if numericas:
                nota_final = round(sum(numericas) / len(numericas), 2)
                aprobado_final = nota_final >= umbral["umbral_pct"]
            else:
                nota_final = None
                aprobado_final = todas_aprobadas

            notas.append(NotaFinalDTO(
                entrada_padron_id=entrada.id,
                nombre=entrada.nombre,
                apellidos=entrada.apellidos,
                email=entrada.email or "",
                comision=entrada.comision,
                regional=entrada.regional,
                nota_final=nota_final,
                aprobado_final=aprobado_final,
                calificaciones=cal_items,
            ))

        return NotasFinalesResponse(
            materia_id=materia_id,
            notas=notas,
        )

    async def get_sin_corregir(
        self, materia_id: uuid.UUID, reporte_token: str,
    ) -> "SinCorregirResponse":
        from app.schemas.analisis import EntregaSinCorregirDTO, SinCorregirResponse
        from app.services.calificaciones_service import CalificacionesService

        preview = CalificacionesService._preview_cache.get(reporte_token)
        if preview is None:
            from fastapi import HTTPException
            raise HTTPException(status_code=404, detail="Reporte de finalizacion no encontrado o expirado")

        calificaciones = await self._cal_repo.get_calificaciones_by_materia(materia_id)

        columns = preview.get("columns", [])
        actividades_textuales: set[str] = set()
        if columns:
            for col in columns:
                nombre_col = col["name"]
                if nombre_col in ("Nombre", "Apellidos", "nombre", "apellidos"):
                    continue
                if col.get("tipo") == "textual":
                    actividades_textuales.add(nombre_col)
        else:
            actividades_textuales = {
                c.actividad for c in calificaciones if c.nota_textual is not None
            }
            if not actividades_textuales:
                actividades_textuales = {
                    c.actividad for c in calificaciones if c.nota_numerica is None
                }

        entradas = {e for e in await self._get_entradas_activas(materia_id)}
        entradas_index: dict[str, EntradaPadron] = {}
        for e in entradas:
            key = f"{e.nombre.lower().strip()}|{e.apellidos.lower().strip()}"
            entradas_index[key] = e

        rows = preview.get("rows", [])
        entregas: list[EntregaSinCorregirDTO] = []

        for row in rows:
            nombre = row.get("Nombre", row.get("nombre", "")).strip()
            apellidos = row.get("Apellidos", row.get("apellidos", "")).strip()
            key = f"{nombre.lower()}|{apellidos.lower()}"
            entrada = entradas_index.get(key)
            if entrada is None:
                continue

            for actividad in actividades_textuales:
                valor = row.get(actividad, "")
                if not valor:
                    continue
                tiene_cal = any(
                    c.entrada_padron_id == entrada.id and c.actividad == actividad
                    for c in calificaciones
                )
                if not tiene_cal:
                    entregas.append(EntregaSinCorregirDTO(
                        entrada_padron_id=entrada.id,
                        nombre=entrada.nombre,
                        apellidos=entrada.apellidos,
                        email=entrada.email or "",
                        comision=entrada.comision,
                        actividad=actividad,
                    ))

        return SinCorregirResponse(
            materia_id=materia_id,
            total_sin_corregir=len(entregas),
            entregas=entregas,
        )

