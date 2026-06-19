import logging
import uuid
from collections import defaultdict
from datetime import date

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import action_codes
from app.models.audit_log import AuditLog
from app.models.liquidacion import EstadoLiquidacion, Liquidacion
from app.repositories.asignacion_repository import AsignacionRepository
from app.repositories.liquidacion_repository import LiquidacionRepository
from app.repositories.salario_base_repository import SalarioBaseRepository
from app.repositories.salario_plus_repository import SalarioPlusRepository
from app.schemas.liquidacion import (
    LiquidacionCalcularResponse,
    LiquidacionCerrarResponse,
    LiquidacionResponse,
    LiquidacionSegmentadaResponse,
)

logger = logging.getLogger(__name__)


class LiquidacionService:
    def __init__(self, session: AsyncSession, tenant_id: uuid.UUID) -> None:
        self._session = session
        self._tenant_id = tenant_id
        self._liquidacion_repo = LiquidacionRepository(session, tenant_id)
        self._asignacion_repo = AsignacionRepository(session, tenant_id)
        self._salario_base_repo = SalarioBaseRepository(session, tenant_id)
        self._salario_plus_repo = SalarioPlusRepository(session, tenant_id)

    @staticmethod
    def _primer_dia(periodo: str) -> date:
        anio, mes = periodo.split("-")
        return date(int(anio), int(mes), 1)

    @staticmethod
    def _es_vigente_en_fecha(asignacion, fecha: date) -> bool:
        return asignacion.desde <= fecha and (
            asignacion.hasta is None or asignacion.hasta >= fecha
        )

    def _to_response(self, l: Liquidacion) -> LiquidacionResponse:
        return LiquidacionResponse(
            id=l.id,
            tenant_id=l.tenant_id,
            cohorte_id=l.cohorte_id,
            periodo=l.periodo,
            usuario_id=l.usuario_id,
            rol=str(l.rol),
            comisiones=l.comisiones,
            monto_base=float(l.monto_base),
            monto_plus=float(l.monto_plus),
            total=float(l.total),
            es_nexo=l.es_nexo,
            excluido_por_factura=l.excluido_por_factura,
            estado=l.estado.value,
            created_at=l.created_at,
            updated_at=l.updated_at,
        )

    async def _run(self, coro):
        try:
            return await coro
        except IntegrityError as exc:
            await self._session.rollback()
            logger.warning("IntegrityError: %s", exc)
            raise HTTPException(
                status_code=409, detail="Conflicto de integridad."
            ) from exc

    async def _commit(self) -> None:
        try:
            await self._session.commit()
        except IntegrityError as exc:
            await self._session.rollback()
            logger.warning("IntegrityError: %s", exc)
            raise HTTPException(
                status_code=409, detail="Conflicto de integridad."
            ) from exc

    async def calcular(
        self, cohorte_id: uuid.UUID, periodo: str, usuario_id: uuid.UUID,
    ) -> LiquidacionCalcularResponse:
        fecha = self._primer_dia(periodo)

        asignaciones = await self._asignacion_repo.list_with_joins(
            cohorte_id=cohorte_id,
        )
        vigentes = [a for a in asignaciones if self._es_vigente_en_fecha(a, fecha)]

        advertencias: list[dict] = []
        asignaciones_por_docente: dict[uuid.UUID, list] = defaultdict(list)
        for a in vigentes:
            asignaciones_por_docente[a.usuario_id].append(a)

        liquidaciones_creadas = []

        for uid, asigns in asignaciones_por_docente.items():
            usuario = asigns[0].usuario if asigns and asigns[0].usuario else None

            existe = await self._liquidacion_repo.get_by_usuario_cohorte_periodo(
                uid, cohorte_id, periodo,
            )
            if existe and existe.estado == EstadoLiquidacion.CERRADA:
                continue
            if existe and existe.estado == EstadoLiquidacion.ABIERTA:
                await self._liquidacion_repo.soft_delete(existe.id)

            cbu_raw = getattr(usuario, 'cbu_encrypted', None) if usuario else None
            alias_raw = getattr(usuario, 'alias_cbu_encrypted', None) if usuario else None
            if not cbu_raw and not alias_raw:
                advertencias.append({
                    "usuario_id": str(uid),
                    "motivo": "Docente sin CBU ni alias CBU — omitido del cálculo",
                })
                continue

            roles_asignados: set[str] = {
                a.rol.nombre for a in asigns if a.rol
            }

            monto_base = 0.0
            rol_base = None
            for rol_nombre in roles_asignados:
                sb = await self._salario_base_repo.get_vigente(rol_nombre, fecha)
                if sb and sb.monto > monto_base:
                    monto_base = float(sb.monto)
                    rol_base = sb.rol.value

            if monto_base == 0.0:
                advertencias.append({
                    "usuario_id": str(uid),
                    "motivo": "Sin SalarioBase vigente — omitido del cálculo",
                })
                continue

            comisiones_por_grupo_rol: dict[tuple[str, str], int] = defaultdict(int)
            comisiones_detalle: list[dict] = []

            for asign in asigns:
                materia = asign.materia
                grupo = materia.grupo_plus if materia else None
                rol_nombre = asign.rol.nombre if asign.rol else None
                n = len(asign.comisiones) if asign.comisiones else 0

                comisiones_detalle.append({
                    "asignacion_id": str(asign.id),
                    "materia_id": str(asign.materia_id) if asign.materia_id else None,
                    "rol": rol_nombre,
                    "grupo_plus": grupo,
                    "comisiones": asign.comisiones,
                })

                if grupo and rol_nombre:
                    comisiones_por_grupo_rol[(grupo, rol_nombre)] += n

            monto_plus = 0.0
            for (grupo, rol_nombre), n_comisiones in comisiones_por_grupo_rol.items():
                sp = await self._salario_plus_repo.get_vigente(
                    grupo, rol_nombre, fecha,
                )
                if sp:
                    monto_plus += float(sp.monto) * n_comisiones

            es_nexo = (
                "NEXO" in roles_asignados
                and len(roles_asignados - {"NEXO"}) == 0
            )
            excluido_por_factura = (
                getattr(usuario, 'facturador', False) if usuario else False
            )

            total = monto_base + monto_plus

            liquidacion = Liquidacion(
                cohorte_id=cohorte_id,
                periodo=periodo,
                usuario_id=uid,
                rol=rol_base if rol_base else sorted(roles_asignados)[0],
                comisiones=comisiones_detalle,
                monto_base=monto_base,
                monto_plus=monto_plus,
                total=total,
                es_nexo=es_nexo,
                excluido_por_factura=excluido_por_factura,
                estado=EstadoLiquidacion.ABIERTA,
            )
            result = await self._run(self._liquidacion_repo.create(liquidacion))
            liquidaciones_creadas.append(result)

        self._log_audit(
            usuario_id, action_codes.LIQUIDACION_CALCULAR,
            {
                "cohorte_id": str(cohorte_id),
                "periodo": periodo,
                "cantidad": len(liquidaciones_creadas),
                "advertencias": len(advertencias),
            },
            len(liquidaciones_creadas),
        )
        await self._commit()

        return LiquidacionCalcularResponse(
            liquidaciones=[self._to_response(l) for l in liquidaciones_creadas],
            advertencias=advertencias,
        )

    async def listar_segmentado(
        self, cohorte_id: uuid.UUID, periodo: str,
    ) -> LiquidacionSegmentadaResponse:
        liquidaciones = await self._liquidacion_repo.list_by_cohorte_periodo(
            cohorte_id, periodo,
        )
        general = []
        nexo = []
        facturantes = []
        total_sin_factura = 0.0
        total_con_factura = 0.0

        for l in liquidaciones:
            dto = self._to_response(l)
            if l.excluido_por_factura:
                facturantes.append(dto)
                total_con_factura += float(l.total)
            elif l.es_nexo:
                nexo.append(dto)
                total_sin_factura += float(l.total)
                total_con_factura += float(l.total)
            else:
                general.append(dto)
                total_sin_factura += float(l.total)
                total_con_factura += float(l.total)

        return LiquidacionSegmentadaResponse(
            general=general,
            nexo=nexo,
            facturantes=facturantes,
            total_sin_factura=total_sin_factura,
            total_con_factura=total_con_factura,
        )

    async def get_detalle(self, liquidacion_id: uuid.UUID) -> LiquidacionResponse:
        l = await self._liquidacion_repo.get(liquidacion_id)
        if l is None:
            raise HTTPException(status_code=404, detail="Liquidación no encontrada.")
        return self._to_response(l)

    async def recalcular(
        self, liquidacion_id: uuid.UUID, usuario_id: uuid.UUID,
    ) -> LiquidacionResponse:
        liq = await self._liquidacion_repo.get(liquidacion_id)
        if liq is None:
            raise HTTPException(status_code=404, detail="Liquidación no encontrada.")
        if liq.estado == EstadoLiquidacion.CERRADA:
            raise HTTPException(
                status_code=409,
                detail="Liquidación cerrada no puede recalcularse.",
            )

        fecha = self._primer_dia(liq.periodo)

        asignaciones = await self._asignacion_repo.list_with_joins(
            cohorte_id=liq.cohorte_id, usuario_id=liq.usuario_id,
        )
        vigentes = [a for a in asignaciones if self._es_vigente_en_fecha(a, fecha)]

        if not vigentes:
            raise HTTPException(
                status_code=422,
                detail="No hay asignaciones vigentes para recalcular.",
            )

        roles_asignados: set[str] = {
            a.rol.nombre for a in vigentes if a.rol
        }

        monto_base = 0.0
        rol_base = None
        for rol_nombre in roles_asignados:
            sb = await self._salario_base_repo.get_vigente(rol_nombre, fecha)
            if sb and sb.monto > monto_base:
                monto_base = float(sb.monto)
                rol_base = sb.rol.value

        if monto_base == 0.0:
            raise HTTPException(
                status_code=422,
                detail="Sin SalarioBase vigente para recalcular.",
            )

        comisiones_por_grupo_rol: dict[tuple[str, str], int] = defaultdict(int)
        comisiones_detalle: list[dict] = []

        for asign in vigentes:
            materia = asign.materia
            grupo = materia.grupo_plus if materia else None
            rol_nombre = asign.rol.nombre if asign.rol else None
            n = len(asign.comisiones) if asign.comisiones else 0

            comisiones_detalle.append({
                "asignacion_id": str(asign.id),
                "materia_id": str(asign.materia_id) if asign.materia_id else None,
                "rol": rol_nombre,
                "grupo_plus": grupo,
                "comisiones": asign.comisiones,
            })

            if grupo and rol_nombre:
                comisiones_por_grupo_rol[(grupo, rol_nombre)] += n

        monto_plus = 0.0
        for (grupo, rol_nombre), n_comisiones in comisiones_por_grupo_rol.items():
            sp = await self._salario_plus_repo.get_vigente(grupo, rol_nombre, fecha)
            if sp:
                monto_plus += float(sp.monto) * n_comisiones

        total = monto_base + monto_plus
        liq.rol = rol_base if rol_base else sorted(roles_asignados)[0]
        liq.comisiones = comisiones_detalle
        liq.monto_base = monto_base
        liq.monto_plus = monto_plus
        liq.total = total

        await self._run(self._liquidacion_repo.update(liq))
        self._log_audit(
            usuario_id, action_codes.LIQUIDACION_CALCULAR,
            {"liquidacion_id": str(liq.id), "accion": "recalcular"},
        )
        await self._commit()
        return self._to_response(liq)

    async def cerrar(
        self, cohorte_id: uuid.UUID, periodo: str, usuario_id: uuid.UUID,
    ) -> LiquidacionCerrarResponse:
        abiertas = await self._liquidacion_repo.list_abiertas_by_cohorte_periodo(
            cohorte_id, periodo,
        )
        if not abiertas:
            raise HTTPException(
                status_code=404,
                detail="No hay liquidaciones abiertas para cerrar.",
            )

        cantidad = await self._liquidacion_repo.cerrar_lote(cohorte_id, periodo)

        self._log_audit(
            usuario_id, action_codes.LIQUIDACION_CERRAR,
            {
                "cohorte_id": str(cohorte_id),
                "periodo": periodo,
                "cantidad": cantidad,
            },
            cantidad,
        )
        await self._commit()

        return LiquidacionCerrarResponse(
            cohorte_id=cohorte_id, periodo=periodo, cantidad_cerradas=cantidad,
        )

    async def historial(
        self,
        cohorte_id: uuid.UUID | None = None,
        periodo: str | None = None,
        usuario_id: uuid.UUID | None = None,
    ) -> list[LiquidacionResponse]:
        stmt = select(Liquidacion).where(
            Liquidacion.tenant_id == self._tenant_id,
            Liquidacion.deleted_at.is_(None),
        )
        if cohorte_id is not None:
            stmt = stmt.where(Liquidacion.cohorte_id == cohorte_id)
        if periodo is not None:
            stmt = stmt.where(Liquidacion.periodo == periodo)
        if usuario_id is not None:
            stmt = stmt.where(Liquidacion.usuario_id == usuario_id)

        stmt = stmt.order_by(Liquidacion.created_at.desc())
        result = await self._session.execute(stmt)
        liquidaciones = result.scalars().all()
        return [self._to_response(l) for l in liquidaciones]

    def _log_audit(
        self,
        usuario_id: uuid.UUID,
        accion: str,
        detalle: dict | None = None,
        filas: int = 0,
    ) -> None:
        record = AuditLog(
            actor_id=usuario_id,
            tenant_id=self._tenant_id,
            accion=accion,
            detalle=detalle,
            filas_afectadas=filas,
        )
        self._session.add(record)
