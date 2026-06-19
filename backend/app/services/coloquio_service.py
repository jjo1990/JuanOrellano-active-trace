import uuid
from datetime import datetime, timedelta

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.evaluacion import Evaluacion
from app.models.materia import Materia
from app.models.cohorte import Cohorte
from app.models.reserva_evaluacion import ReservaEvaluacion
from app.models.resultado_evaluacion import ResultadoEvaluacion
from app.models.user import User
from app.repositories.evaluacion_repository import EvaluacionRepository
from app.repositories.reserva_evaluacion_repository import ReservaEvaluacionRepository
from app.repositories.resultado_evaluacion_repository import ResultadoEvaluacionRepository
from app.schemas.coloquio import (
    AgendaFilterParams,
    AlumnoInfo,
    EvaluacionCreateRequest,
    EvaluacionDetailResponse,
    EvaluacionResponse,
    EvaluacionUpdateRequest,
    ImportAlumnosRequest,
    MetricasResponse,
    ReservaAgendaResponse,
    ReservaCreateRequest,
    ReservaInfo,
    ReservaResponse,
    ResultadoConsolidadoResponse,
    ResultadoCreateRequest,
    ResultadoResponse,
    ResultadosFilterParams,
)


class ColoquioService:
    def __init__(self, session: AsyncSession, tenant_id: uuid.UUID) -> None:
        self._session = session
        self._tenant_id = tenant_id
        self._eval_repo = EvaluacionRepository(session, tenant_id)
        self._reserva_repo = ReservaEvaluacionRepository(session, tenant_id)
        self._resultado_repo = ResultadoEvaluacionRepository(session, tenant_id)

    async def crear_evaluacion(
        self, data: EvaluacionCreateRequest, tenant_id: uuid.UUID,
    ) -> Evaluacion:
        evaluacion = Evaluacion(
            materia_id=data.materia_id,
            cohorte_id=data.cohorte_id,
            tipo=data.tipo,
            instancia=data.instancia,
            dias_disponibles=data.dias_disponibles,
            cupos_por_dia=data.cupos_por_dia,
            estado="Activa",
        )
        evaluacion = await self._eval_repo.create(evaluacion)
        return evaluacion

    async def editar_evaluacion(
        self, evaluacion_id: uuid.UUID, data: EvaluacionUpdateRequest, tenant_id: uuid.UUID,
    ) -> Evaluacion:
        evaluacion = await self._eval_repo.get_by_id(evaluacion_id, tenant_id)
        if evaluacion is None:
            raise HTTPException(status_code=404, detail="Evaluacion no encontrada.")
        if data.estado is not None:
            evaluacion.estado = data.estado
        if data.cupos_por_dia is not None:
            evaluacion.cupos_por_dia = data.cupos_por_dia
        if data.dias_disponibles is not None:
            evaluacion.dias_disponibles = data.dias_disponibles
        await self._session.flush()
        return evaluacion

    async def get_evaluacion(
        self, evaluacion_id: uuid.UUID, tenant_id: uuid.UUID,
    ) -> EvaluacionDetailResponse:
        evaluacion = await self._eval_repo.get_by_id(evaluacion_id, tenant_id)
        if evaluacion is None:
            raise HTTPException(status_code=404, detail="Evaluacion no encontrada.")

        resultados = await self._resultado_repo.list_by_evaluacion(evaluacion_id, tenant_id)
        reservas = await self._reserva_repo.list_by_evaluacion(evaluacion_id, tenant_id)

        reservas_activas = sum(1 for r in reservas if r.estado == "Activa")

        alumnos: list[AlumnoInfo] = []
        for resultado in resultados:
            user = await self._get_user(resultado.alumno_id)
            if user:
                alumnos.append(AlumnoInfo(
                    id=user.id,
                    nombre=user.nombre,
                    apellidos=user.apellidos,
                    email=user.email,
                    legajo=user.legajo,
                ))

        reservas_info: list[ReservaInfo] = [
            ReservaInfo(
                id=r.id,
                evaluacion_id=r.evaluacion_id,
                alumno_id=r.alumno_id,
                fecha_hora=r.fecha_hora,
                estado=r.estado,
                created_at=r.created_at,
            )
            for r in reservas
        ]

        materias = await self._eval_repo.list_by_materia(evaluacion.materia_id, tenant_id)
        otras_eval = [e for e in materias if e.id != evaluacion.id]
        cupos_libres = evaluacion.cupos_por_dia - max(
            self._max_reservas_por_dia(reservas_activas, reservas, evaluacion.cupos_por_dia), 0,
        )

        return EvaluacionDetailResponse(
            id=evaluacion.id,
            materia_id=evaluacion.materia_id,
            cohorte_id=evaluacion.cohorte_id,
            tipo=evaluacion.tipo,
            instancia=evaluacion.instancia,
            dias_disponibles=evaluacion.dias_disponibles,
            cupos_por_dia=evaluacion.cupos_por_dia,
            estado=evaluacion.estado,
            created_at=evaluacion.created_at,
            total_alumnos=len(alumnos),
            reservas_activas=reservas_activas,
            cupos_libres=cupos_libres,
            alumnos=alumnos,
            reservas=reservas_info,
        )

    async def list_evaluaciones(
        self, tenant_id: uuid.UUID, cohorte_id: uuid.UUID | None = None,
    ) -> list[EvaluacionResponse]:
        if cohorte_id is not None:
            evaluaciones = await self._eval_repo.list_by_cohorte(cohorte_id, tenant_id)
        else:
            evaluaciones = await self._eval_repo.list_all(tenant_id)

        result: list[EvaluacionResponse] = []
        for ev in evaluaciones:
            resultados = await self._resultado_repo.list_by_evaluacion(ev.id, tenant_id)
            reservas = await self._reserva_repo.list_by_evaluacion(ev.id, tenant_id)
            reservas_activas = sum(1 for r in reservas if r.estado == "Activa")
            cupos_libres = ev.cupos_por_dia - self._max_reservas_por_dia(
                reservas_activas, reservas, ev.cupos_por_dia,
            )

            result.append(EvaluacionResponse(
                id=ev.id,
                materia_id=ev.materia_id,
                cohorte_id=ev.cohorte_id,
                tipo=ev.tipo,
                instancia=ev.instancia,
                dias_disponibles=ev.dias_disponibles,
                cupos_por_dia=ev.cupos_por_dia,
                estado=ev.estado,
                created_at=ev.created_at,
                total_alumnos=len(resultados),
                reservas_activas=reservas_activas,
                cupos_libres=cupos_libres,
            ))
        return result

    async def importar_alumnos(
        self, evaluacion_id: uuid.UUID, data: ImportAlumnosRequest, tenant_id: uuid.UUID,
    ) -> int:
        evaluacion = await self._eval_repo.get_by_id(evaluacion_id, tenant_id)
        if evaluacion is None:
            raise HTTPException(status_code=404, detail="Evaluacion no encontrada.")

        importados = 0
        for item in data.alumnos:
            existente = await self._resultado_repo.get_by_alumno_evaluacion(
                evaluacion_id, item.user_id,
            )
            if existente is not None:
                continue
            resultado = ResultadoEvaluacion(
                evaluacion_id=evaluacion_id,
                alumno_id=item.user_id,
                nota_final=None,
            )
            await self._resultado_repo.create(resultado)
            importados += 1

        return importados

    async def reservar_turno(
        self, data: ReservaCreateRequest, tenant_id: uuid.UUID, alumno_id: uuid.UUID,
    ) -> ReservaEvaluacion:
        evaluacion = await self._eval_repo.get_by_id(data.evaluacion_id, tenant_id)
        if evaluacion is None:
            raise HTTPException(status_code=404, detail="Evaluacion no encontrada.")

        if evaluacion.estado == "Cerrada":
            raise HTTPException(status_code=422, detail="La convocatoria está cerrada.")

        activa_existente = await self._reserva_repo.get_activa_por_alumno_evaluacion(
            data.evaluacion_id, alumno_id,
        )
        if activa_existente is not None:
            raise HTTPException(
                status_code=409, detail="Ya tenés una reserva activa en esta convocatoria.",
            )

        count = await self._reserva_repo.count_activas_por_fecha(
            data.evaluacion_id, data.fecha_hora,
        )
        if count >= evaluacion.cupos_por_dia:
            raise HTTPException(status_code=409, detail="Cupo agotado para esta fecha.")

        reserva = ReservaEvaluacion(
            evaluacion_id=data.evaluacion_id,
            alumno_id=alumno_id,
            fecha_hora=data.fecha_hora,
            estado="Activa",
        )
        reserva = await self._reserva_repo.create(reserva)
        return reserva

    async def cancelar_reserva(
        self, reserva_id: uuid.UUID, tenant_id: uuid.UUID,
        user_id: uuid.UUID, is_coordinador: bool = False,
    ) -> None:
        reserva = await self._reserva_repo.get_by_id(reserva_id, tenant_id)
        if reserva is None:
            raise HTTPException(status_code=404, detail="Reserva no encontrada.")

        if reserva.estado == "Cancelada":
            raise HTTPException(status_code=422, detail="La reserva ya está cancelada.")

        if not is_coordinador and reserva.alumno_id != user_id:
            raise HTTPException(status_code=403, detail="No podés cancelar una reserva ajena.")

        await self._reserva_repo.cancelar(reserva_id)

    async def registrar_resultado(
        self, data: ResultadoCreateRequest, tenant_id: uuid.UUID,
    ) -> ResultadoEvaluacion:
        resultado = await self._resultado_repo.get_by_alumno_evaluacion(
            data.evaluacion_id, data.alumno_id,
        )
        if resultado is None:
            raise HTTPException(
                status_code=404, detail="El alumno no está en la convocatoria.",
            )

        resultado.nota_final = data.nota_final
        await self._session.flush()
        return resultado

    async def get_resultados(
        self, tenant_id: uuid.UUID, filtros: ResultadosFilterParams,
    ) -> list[ResultadoConsolidadoResponse]:
        if filtros.materia_id is not None:
            evaluaciones = await self._eval_repo.list_by_materia(filtros.materia_id, tenant_id)
            evaluaciones_ids = [e.id for e in evaluaciones]
        else:
            evaluaciones = await self._eval_repo.list_all(tenant_id)
            evaluaciones_ids = [e.id for e in evaluaciones]

        resultados: list[ResultadoEvaluacion] = []
        for eid in evaluaciones_ids:
            res = await self._resultado_repo.list_by_evaluacion(eid, tenant_id)
            if filtros.pendientes:
                res = [r for r in res if r.nota_final is None]
            resultados.extend(res)

        result: list[ResultadoConsolidadoResponse] = []
        for r in resultados:
            ev = next((e for e in evaluaciones if e.id == r.evaluacion_id), None)
            user = await self._get_user(r.alumno_id)

            materia_nombre = ""
            cohorte_nombre = ""
            if ev is not None:
                mat = await self._session.get(Materia, ev.materia_id)
                if mat:
                    materia_nombre = mat.nombre
                coh = await self._session.get(Cohorte, ev.cohorte_id)
                if coh:
                    cohorte_nombre = coh.nombre

            result.append(ResultadoConsolidadoResponse(
                id=r.id,
                evaluacion_id=r.evaluacion_id,
                alumno_id=r.alumno_id,
                nota_final=r.nota_final,
                created_at=r.created_at,
                updated_at=r.updated_at,
                alumno_nombre=f"{user.nombre} {user.apellidos}" if user else "",
                alumno_legajo=user.legajo if user else None,
                materia_nombre=materia_nombre,
                cohorte_nombre=cohorte_nombre,
                tipo_evaluacion=ev.tipo if ev else "",
                instancia=ev.instancia if ev else "",
            ))
        return result

    async def get_agenda(
        self, tenant_id: uuid.UUID, filtros: AgendaFilterParams,
    ) -> list[ReservaAgendaResponse]:
        evaluaciones = await self._eval_repo.list_all(tenant_id)
        eval_map = {e.id: e for e in evaluaciones}

        reservas: list[ReservaEvaluacion] = []
        for ev_id in eval_map:
            ev_reservas = await self._reserva_repo.list_by_evaluacion(
                ev_id, tenant_id, estado="Activa",
            )
            reservas.extend(ev_reservas)

        if filtros.materia_id is not None:
            ids_con_materia = {
                e.id for e in evaluaciones if e.materia_id == filtros.materia_id
            }
            reservas = [r for r in reservas if r.evaluacion_id in ids_con_materia]

        if filtros.cohorte_id is not None:
            ids_con_cohorte = {
                e.id for e in evaluaciones if e.cohorte_id == filtros.cohorte_id
            }
            reservas = [r for r in reservas if r.evaluacion_id in ids_con_cohorte]

        if filtros.fecha_desde is not None:
            reservas = [r for r in reservas if r.fecha_hora >= filtros.fecha_desde]
        if filtros.fecha_hasta is not None:
            reservas = [r for r in reservas if r.fecha_hora <= filtros.fecha_hasta]

        if filtros.q is not None:
            q_lower = filtros.q.lower()
            filtered: list[ReservaEvaluacion] = []
            for r in reservas:
                user = await self._get_user(r.alumno_id)
                if user and (
                    q_lower in user.nombre.lower()
                    or q_lower in user.apellidos.lower()
                    or (user.legajo and q_lower in user.legajo.lower())
                ):
                    filtered.append(r)
            reservas = filtered

        result: list[ReservaAgendaResponse] = []
        for r in reservas:
            ev = eval_map.get(r.evaluacion_id)
            user = await self._get_user(r.alumno_id)
            mat = await self._session.get(Materia, ev.materia_id) if ev else None
            coh = await self._session.get(Cohorte, ev.cohorte_id) if ev else None

            result.append(ReservaAgendaResponse(
                id=r.id,
                evaluacion_id=r.evaluacion_id,
                alumno_id=r.alumno_id,
                fecha_hora=r.fecha_hora,
                estado=r.estado,
                created_at=r.created_at,
                alumno_nombre=f"{user.nombre} {user.apellidos}" if user else "",
                alumno_legajo=user.legajo if user else None,
                materia_nombre=mat.nombre if mat else "",
                cohorte_nombre=coh.nombre if coh else "",
            ))
        return result

    async def get_metricas(
        self, tenant_id: uuid.UUID, cohorte_id: uuid.UUID | None = None,
    ) -> MetricasResponse:
        evaluaciones = await self._eval_repo.list_all(tenant_id)
        if cohorte_id is not None:
            evaluaciones = [e for e in evaluaciones if e.cohorte_id == cohorte_id]

        total_alumnos_cargados = 0
        total_reservas_activas = 0
        total_notas_registradas = 0
        total_instancias_activas = sum(1 for e in evaluaciones if e.estado == "Activa")

        for ev in evaluaciones:
            resultados = await self._resultado_repo.list_by_evaluacion(ev.id, tenant_id)
            total_alumnos_cargados += len(resultados)
            total_notas_registradas += sum(1 for r in resultados if r.nota_final is not None)

            reservas = await self._reserva_repo.list_by_evaluacion(
                ev.id, tenant_id, estado="Activa",
            )
            total_reservas_activas += len(reservas)

        return MetricasResponse(
            total_alumnos_cargados=total_alumnos_cargados,
            total_instancias_activas=total_instancias_activas,
            total_reservas_activas=total_reservas_activas,
            total_notas_registradas=total_notas_registradas,
        )

    async def get_resultados_self(
        self, tenant_id: uuid.UUID, alumno_id: uuid.UUID,
    ) -> list[ResultadoConsolidadoResponse]:
        evaluaciones = await self._eval_repo.list_all(tenant_id)
        result: list[ResultadoConsolidadoResponse] = []
        for ev in evaluaciones:
            resultado = await self._resultado_repo.get_by_alumno_evaluacion(ev.id, alumno_id)
            if resultado is not None:
                mat = await self._session.get(Materia, ev.materia_id)
                coh = await self._session.get(Cohorte, ev.cohorte_id)
                result.append(ResultadoConsolidadoResponse(
                    id=resultado.id,
                    evaluacion_id=resultado.evaluacion_id,
                    alumno_id=resultado.alumno_id,
                    nota_final=resultado.nota_final,
                    created_at=resultado.created_at,
                    updated_at=resultado.updated_at,
                    materia_nombre=mat.nombre if mat else "",
                    cohorte_nombre=coh.nombre if coh else "",
                    tipo_evaluacion=ev.tipo,
                    instancia=ev.instancia,
                ))
        return result

    def _max_reservas_por_dia(
        self, reservas_activas: int, reservas: list[ReservaEvaluacion], cupos_por_dia: int,
    ) -> int:
        counts: dict[str, int] = {}
        for r in reservas:
            if r.estado == "Activa":
                key = r.fecha_hora.strftime("%Y-%m-%d")
                counts[key] = counts.get(key, 0) + 1
        return max(counts.values()) if counts else 0

    async def _get_user(self, user_id: uuid.UUID) -> User | None:
        stmt = select(User).where(
            User.id == user_id,
            User.tenant_id == self._tenant_id,
            User.deleted_at.is_(None),
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()
