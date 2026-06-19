import csv
import io
import logging
import uuid
from datetime import date

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.asignacion import Asignacion
from app.models.carrera import Carrera
from app.models.cohorte import Cohorte
from app.models.materia import Materia
from app.models.rol import Rol
from app.models.user import User
from app.repositories.asignacion_repository import AsignacionRepository
from app.repositories.user_repository import UserRepository
from app.schemas.equipo import (
    AsignacionMasivaRequest,
    AsignacionMasivaResponse,
    BuscarUsuariosParams,
    ClonarEquipoRequest,
    ClonarEquipoResponse,
    ErrorIndividual,
    ExportarEquipoParams,
    MisEquiposFilterParams,
    MisEquiposResponse,
    ModificarVigenciaRequest,
    ModificarVigenciaResponse,
    UsuarioAutocompletadoResponse,
)

logger = logging.getLogger(__name__)

CSV_HEADERS = [
    "nombre", "apellido", "email", "legajo", "rol", "materia",
    "carrera", "cohorte", "comisiones", "desde", "hasta", "estado",
]


class EquipoService:
    def __init__(self, session: AsyncSession, tenant_id: uuid.UUID) -> None:
        self._session = session
        self._tenant_id = tenant_id
        self._asig_repo = AsignacionRepository(session, tenant_id)
        self._user_repo = UserRepository(session, tenant_id)

    async def _run(self, coro):
        try:
            result = await coro
            return result
        except IntegrityError as exc:
            await self._session.rollback()
            logger.warning("IntegrityError: %s", exc)
            raise HTTPException(
                status_code=409,
                detail="El recurso ya existe o viola una restriccion de unicidad.",
            ) from exc

    async def _commit(self) -> None:
        try:
            await self._session.commit()
        except IntegrityError as exc:
            await self._session.rollback()
            logger.warning("IntegrityError: %s", exc)
            raise HTTPException(
                status_code=409,
                detail="El recurso ya existe o viola una restriccion de unicidad.",
            ) from exc

    async def _validate_fk(
        self, model_class, entity_id: uuid.UUID | None, label: str,
    ) -> None:
        if entity_id is None:
            return
        stmt = (
            select(model_class)
            .where(
                model_class.id == entity_id,
                model_class.tenant_id == self._tenant_id,
            )
        )
        result = await self._session.execute(stmt)
        if result.scalar_one_or_none() is None:
            raise HTTPException(
                status_code=404,
                detail=f"{label} no encontrada(o) en este tenant.",
            )

    @staticmethod
    def _estado_vigencia(entity: Asignacion) -> str:
        hoy = date.today()
        if entity.desde > hoy:
            return "Vencida"
        if entity.hasta is not None and entity.hasta < hoy:
            return "Vencida"
        return "Vigente"

    @staticmethod
    def _safe_csv_cell(value) -> str:
        s = str(value) if value is not None else ""
        if s and s[0] in ("=", "+", "-", "@"):
            s = "'" + s
        return s

    def _entity_to_mis_equipos(self, entity: Asignacion) -> MisEquiposResponse:
        return MisEquiposResponse(
            id=entity.id,
            usuario_nombre=entity.usuario.nombre if entity.usuario else "",
            usuario_apellidos=entity.usuario.apellidos if entity.usuario else "",
            usuario_email=entity.usuario.email if entity.usuario else "",
            usuario_legajo=entity.usuario.legajo if entity.usuario else None,
            rol_nombre=entity.rol.nombre if entity.rol else "",
            materia_nombre=entity.materia.nombre if entity.materia else None,
            carrera_nombre=entity.carrera.nombre if entity.carrera else None,
            cohorte_nombre=entity.cohorte.nombre if entity.cohorte else None,
            comisiones=entity.comisiones or [],
            desde=entity.desde,
            hasta=entity.hasta,
            estado_vigencia=self._estado_vigencia(entity),
        )

    async def get_mis_equipos(
        self, usuario_id: uuid.UUID, filters: MisEquiposFilterParams,
    ) -> list[MisEquiposResponse]:
        entities = await self._asig_repo.list_with_joins(
            usuario_id=usuario_id,
            materia_id=filters.materia_id,
            rol_id=filters.rol_id,
            carrera_id=filters.carrera_id,
            cohorte_id=filters.cohorte_id,
            vigente=filters.vigente,
        )
        return [self._entity_to_mis_equipos(e) for e in entities]

    async def asignacion_masiva(
        self, data: AsignacionMasivaRequest,
    ) -> AsignacionMasivaResponse:
        creadas = []
        errores = []
        total = len(data.usuarios)

        for item in data.usuarios:
            try:
                await self._validate_fk(User, item.id, "Usuario")
                await self._validate_fk(Rol, data.rol_id, "Rol")
                if data.materia_id:
                    await self._validate_fk(Materia, data.materia_id, "Materia")
                if data.carrera_id:
                    await self._validate_fk(Carrera, data.carrera_id, "Carrera")
                if data.cohorte_id:
                    await self._validate_fk(Cohorte, data.cohorte_id, "Cohorte")
                if data.responsable_id:
                    await self._validate_fk(User, data.responsable_id, "Responsable")

                entity = Asignacion(
                    usuario_id=item.id,
                    rol_id=data.rol_id,
                    materia_id=data.materia_id,
                    carrera_id=data.carrera_id,
                    cohorte_id=data.cohorte_id,
                    comisiones=data.comisiones,
                    responsable_id=data.responsable_id,
                    desde=data.desde,
                    hasta=data.hasta,
                )
                entity.tenant_id = self._tenant_id
                self._session.add(entity)
                await self._session.flush()
                await self._session.refresh(entity)

                creadas.append({
                    "id": str(entity.id),
                    "tenant_id": str(entity.tenant_id) if entity.tenant_id else None,
                    "usuario_id": str(entity.usuario_id),
                    "rol_id": str(entity.rol_id),
                    "materia_id": str(entity.materia_id) if entity.materia_id else None,
                    "carrera_id": str(entity.carrera_id) if entity.carrera_id else None,
                    "cohorte_id": str(entity.cohorte_id) if entity.cohorte_id else None,
                    "comisiones": entity.comisiones or [],
                    "responsable_id": str(entity.responsable_id) if entity.responsable_id else None,
                    "desde": entity.desde.isoformat(),
                    "hasta": entity.hasta.isoformat() if entity.hasta else None,
                    "created_at": entity.created_at.isoformat() if entity.created_at else None,
                    "updated_at": entity.updated_at.isoformat() if entity.updated_at else None,
                })
            except HTTPException as exc:
                errores.append(ErrorIndividual(
                    usuario_id=item.id,
                    error=exc.detail,
                ))

        return AsignacionMasivaResponse(
            asignaciones_creadas=creadas,
            errores=errores,
            total_procesados=total,
            total_exitosos=len(creadas),
            total_fallidos=len(errores),
        )

    async def clonar_equipo(
        self, data: ClonarEquipoRequest,
    ) -> ClonarEquipoResponse:
        await self._validate_fk(Cohorte, data.cohorte_destino_id, "Cohorte destino")

        origen = await self._asig_repo.list_by_equipo(
            materia_id=data.materia_id,
            carrera_id=data.carrera_id,
            cohorte_id=data.cohorte_origen_id,
        )

        if not origen:
            return ClonarEquipoResponse(asignaciones_creadas=[], total_clonadas=0)

        nuevas = []
        for a in origen:
            nueva = Asignacion(
                usuario_id=a.usuario_id,
                rol_id=a.rol_id,
                materia_id=a.materia_id,
                carrera_id=a.carrera_id,
                cohorte_id=data.cohorte_destino_id,
                comisiones=a.comisiones,
                responsable_id=a.responsable_id,
                desde=data.desde,
                hasta=data.hasta,
            )
            nuevas.append(nueva)

        result = await self._asig_repo.bulk_create(nuevas)
        await self._commit()

        creadas = [{
            "id": str(r.id),
            "tenant_id": str(r.tenant_id) if r.tenant_id else None,
            "usuario_id": str(r.usuario_id),
            "rol_id": str(r.rol_id),
            "materia_id": str(r.materia_id) if r.materia_id else None,
            "carrera_id": str(r.carrera_id) if r.carrera_id else None,
            "cohorte_id": str(r.cohorte_id) if r.cohorte_id else None,
            "comisiones": r.comisiones or [],
            "responsable_id": str(r.responsable_id) if r.responsable_id else None,
            "desde": r.desde.isoformat(),
            "hasta": r.hasta.isoformat() if r.hasta else None,
            "created_at": r.created_at.isoformat() if r.created_at else None,
            "updated_at": r.updated_at.isoformat() if r.updated_at else None,
        } for r in result]

        return ClonarEquipoResponse(
            asignaciones_creadas=creadas,
            total_clonadas=len(result),
        )

    async def modificar_vigencia_bloque(
        self, data: ModificarVigenciaRequest,
    ) -> ModificarVigenciaResponse:
        total_encontradas = await self._asig_repo.list_by_equipo(
            materia_id=data.materia_id,
            carrera_id=data.carrera_id,
            cohorte_id=data.cohorte_id,
        )
        total_count = len(total_encontradas)

        actualizadas = await self._asig_repo.bulk_update_vigencia(
            materia_id=data.materia_id,
            carrera_id=data.carrera_id,
            cohorte_id=data.cohorte_id,
            desde=data.desde,
            hasta=data.hasta,
        )
        await self._commit()

        return ModificarVigenciaResponse(
            asignaciones_actualizadas=actualizadas,
            total_encontradas=total_count,
        )

    async def exportar_equipo(self, filters: ExportarEquipoParams) -> str:
        entities = await self._asig_repo.list_with_joins(
            materia_id=filters.materia_id,
            carrera_id=filters.carrera_id,
            cohorte_id=filters.cohorte_id,
            vigente=filters.vigente,
        )

        output = io.StringIO()
        writer = csv.writer(output)

        writer.writerow(CSV_HEADERS)

        for a in entities:
            usuario = a.usuario
            writer.writerow([
                self._safe_csv_cell(usuario.nombre if usuario else ""),
                self._safe_csv_cell(usuario.apellidos if usuario else ""),
                self._safe_csv_cell(usuario.email if usuario else ""),
                self._safe_csv_cell(usuario.legajo if usuario else ""),
                self._safe_csv_cell(a.rol.nombre if a.rol else ""),
                self._safe_csv_cell(a.materia.nombre if a.materia else ""),
                self._safe_csv_cell(a.carrera.nombre if a.carrera else ""),
                self._safe_csv_cell(a.cohorte.nombre if a.cohorte else ""),
                self._safe_csv_cell(", ".join(a.comisiones) if a.comisiones else ""),
                self._safe_csv_cell(a.desde.isoformat()),
                self._safe_csv_cell(a.hasta.isoformat() if a.hasta else ""),
                self._safe_csv_cell(self._estado_vigencia(a)),
            ])

        return output.getvalue()

    async def buscar_usuarios(
        self, params: BuscarUsuariosParams,
    ) -> list[UsuarioAutocompletadoResponse]:
        roles = None
        if params.roles:
            roles = [r.strip() for r in params.roles.split(",") if r.strip()]

        users = await self._user_repo.search_by_name(
            query=params.q,
            limite=params.limite,
            roles=roles,
        )
        return [
            UsuarioAutocompletadoResponse(
                id=u.id,
                nombre=u.nombre,
                apellidos=u.apellidos,
                email=u.email,
                legajo=u.legajo,
            )
            for u in users
        ]
