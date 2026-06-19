import uuid
from datetime import date

import pytest
from pydantic import ValidationError

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
    UsuarioBulkItem,
)


class TestMisEquiposResponse:
    def test_extra_forbid_rejects_unknown_fields(self):
        with pytest.raises(ValidationError, match="Extra inputs are not permitted"):
            MisEquiposResponse(
                id=uuid.uuid4(),
                usuario_nombre="Juan",
                usuario_apellidos="Perez",
                usuario_email="juan@test.com",
                usuario_legajo="L-001",
                rol_nombre="PROFESOR",
                materia_nombre="Matematicas",
                carrera_nombre="Ingenieria",
                cohorte_nombre="2026-A",
                comisiones=["A", "B"],
                desde=date(2026, 1, 1),
                hasta=date(2026, 12, 31),
                estado_vigencia="Vigente",
                campo_inexistente=123,
            )

    def test_all_required_fields_present(self):
        resp = MisEquiposResponse(
            id=uuid.uuid4(),
            usuario_nombre="Juan",
            usuario_apellidos="Perez",
            usuario_email="juan@test.com",
            usuario_legajo="L-001",
            rol_nombre="PROFESOR",
            materia_nombre="Matematicas",
            carrera_nombre="Ingenieria",
            cohorte_nombre="2026-A",
            comisiones=["A", "B"],
            desde=date(2026, 1, 1),
            hasta=date(2026, 12, 31),
            estado_vigencia="Vigente",
        )
        assert resp.usuario_nombre == "Juan"
        assert resp.usuario_apellidos == "Perez"
        assert resp.comisiones == ["A", "B"]
        assert resp.estado_vigencia == "Vigente"

    def test_hasta_can_be_none(self):
        resp = MisEquiposResponse(
            id=uuid.uuid4(),
            usuario_nombre="Juan",
            usuario_apellidos="Perez",
            usuario_email="juan@test.com",
            usuario_legajo="L-001",
            rol_nombre="PROFESOR",
            materia_nombre="Matematicas",
            carrera_nombre="Ingenieria",
            cohorte_nombre="2026-A",
            comisiones=[],
            desde=date(2026, 1, 1),
            hasta=None,
            estado_vigencia="Vigente",
        )
        assert resp.hasta is None


class TestMisEquiposFilterParams:
    def test_all_fields_optional(self):
        params = MisEquiposFilterParams()
        assert params.vigente is None
        assert params.materia_id is None
        assert params.rol_id is None
        assert params.carrera_id is None
        assert params.cohorte_id is None

    def test_optional_fields_can_be_set(self):
        mid = uuid.uuid4()
        params = MisEquiposFilterParams(vigente=True, materia_id=mid)
        assert params.vigente is True
        assert params.materia_id == mid

    def test_extra_forbid(self):
        with pytest.raises(ValidationError, match="Extra inputs are not permitted"):
            MisEquiposFilterParams(campo_extra="no permitido")


class TestUsuarioBulkItem:
    def test_requires_id(self):
        item = UsuarioBulkItem(id=uuid.uuid4())
        assert isinstance(item.id, uuid.UUID)

    def test_id_required(self):
        with pytest.raises(ValidationError):
            UsuarioBulkItem()

    def test_extra_forbid(self):
        with pytest.raises(ValidationError, match="Extra inputs are not permitted"):
            UsuarioBulkItem(id=uuid.uuid4(), extra=1)


class TestAsignacionMasivaRequest:
    def test_valid_request(self):
        req = AsignacionMasivaRequest(
            usuarios=[UsuarioBulkItem(id=uuid.uuid4())],
            rol_id=uuid.uuid4(),
            desde=date(2026, 1, 1),
            hasta=date(2026, 12, 31),
        )
        assert len(req.usuarios) == 1
        assert req.hasta == date(2026, 12, 31)

    def test_hasta_none_allowed(self):
        req = AsignacionMasivaRequest(
            usuarios=[UsuarioBulkItem(id=uuid.uuid4())],
            rol_id=uuid.uuid4(),
            desde=date(2026, 1, 1),
            hasta=None,
        )
        assert req.hasta is None

    def test_hasta_before_desde_fails(self):
        with pytest.raises(ValidationError, match="posterior o igual"):
            AsignacionMasivaRequest(
                usuarios=[UsuarioBulkItem(id=uuid.uuid4())],
                rol_id=uuid.uuid4(),
                desde=date(2026, 12, 31),
                hasta=date(2026, 1, 1),
            )

    def test_hasta_equal_desde_ok(self):
        req = AsignacionMasivaRequest(
            usuarios=[UsuarioBulkItem(id=uuid.uuid4())],
            rol_id=uuid.uuid4(),
            desde=date(2026, 6, 15),
            hasta=date(2026, 6, 15),
        )
        assert req.desde == req.hasta

    def test_empty_usuarios_fails(self):
        with pytest.raises(ValidationError):
            AsignacionMasivaRequest(
                usuarios=[],
                rol_id=uuid.uuid4(),
                desde=date(2026, 1, 1),
            )

    def test_extra_forbid(self):
        with pytest.raises(ValidationError, match="Extra inputs are not permitted"):
            AsignacionMasivaRequest(
                usuarios=[UsuarioBulkItem(id=uuid.uuid4())],
                rol_id=uuid.uuid4(),
                desde=date(2026, 1, 1),
                campo_extra="no",
            )


class TestErrorIndividual:
    def test_valid(self):
        uid = uuid.uuid4()
        error = ErrorIndividual(usuario_id=uid, error="Usuario no encontrado")
        assert error.usuario_id == uid
        assert error.error == "Usuario no encontrado"

    def test_extra_forbid(self):
        with pytest.raises(ValidationError, match="Extra inputs are not permitted"):
            ErrorIndividual(usuario_id=uuid.uuid4(), error="x", extra=1)


class TestAsignacionMasivaResponse:
    def test_valid_response(self):
        resp = AsignacionMasivaResponse(
            asignaciones_creadas=[],
            errores=[],
            total_procesados=2,
            total_exitosos=2,
            total_fallidos=0,
        )
        assert resp.total_procesados == 2
        assert resp.total_exitosos == 2
        assert resp.total_fallidos == 0

    def test_with_errors(self):
        uid = uuid.uuid4()
        resp = AsignacionMasivaResponse(
            asignaciones_creadas=[],
            errores=[ErrorIndividual(usuario_id=uid, error="Usuario no encontrado")],
            total_procesados=1,
            total_exitosos=0,
            total_fallidos=1,
        )
        assert len(resp.errores) == 1
        assert resp.total_fallidos == 1

    def test_extra_forbid(self):
        with pytest.raises(ValidationError, match="Extra inputs are not permitted"):
            AsignacionMasivaResponse(
                asignaciones_creadas=[],
                errores=[],
                total_procesados=0,
                total_exitosos=0,
                total_fallidos=0,
                extra=1,
            )


class TestClonarEquipoRequest:
    def test_valid_request(self):
        req = ClonarEquipoRequest(
            materia_id=uuid.uuid4(),
            carrera_id=uuid.uuid4(),
            cohorte_origen_id=uuid.uuid4(),
            cohorte_destino_id=uuid.uuid4(),
            desde=date(2026, 8, 1),
            hasta=date(2026, 12, 31),
        )
        assert req.desde == date(2026, 8, 1)

    def test_same_origin_destino_fails(self):
        cid = uuid.uuid4()
        with pytest.raises(ValidationError, match="diferentes"):
            ClonarEquipoRequest(
                materia_id=uuid.uuid4(),
                carrera_id=uuid.uuid4(),
                cohorte_origen_id=cid,
                cohorte_destino_id=cid,
                desde=date(2026, 1, 1),
                hasta=date(2026, 12, 31),
            )

    def test_hasta_before_desde_fails(self):
        with pytest.raises(ValidationError, match="posterior o igual"):
            ClonarEquipoRequest(
                materia_id=uuid.uuid4(),
                carrera_id=uuid.uuid4(),
                cohorte_origen_id=uuid.uuid4(),
                cohorte_destino_id=uuid.uuid4(),
                desde=date(2026, 12, 31),
                hasta=date(2026, 1, 1),
            )

    def test_hasta_none_allowed(self):
        req = ClonarEquipoRequest(
            materia_id=uuid.uuid4(),
            carrera_id=uuid.uuid4(),
            cohorte_origen_id=uuid.uuid4(),
            cohorte_destino_id=uuid.uuid4(),
            desde=date(2026, 1, 1),
            hasta=None,
        )
        assert req.hasta is None

    def test_extra_forbid(self):
        with pytest.raises(ValidationError, match="Extra inputs are not permitted"):
            ClonarEquipoRequest(
                materia_id=uuid.uuid4(),
                carrera_id=uuid.uuid4(),
                cohorte_origen_id=uuid.uuid4(),
                cohorte_destino_id=uuid.uuid4(),
                desde=date(2026, 1, 1),
                extra=1,
            )


class TestClonarEquipoResponse:
    def test_valid(self):
        resp = ClonarEquipoResponse(asignaciones_creadas=[], total_clonadas=3)
        assert resp.total_clonadas == 3

    def test_extra_forbid(self):
        with pytest.raises(ValidationError, match="Extra inputs are not permitted"):
            ClonarEquipoResponse(asignaciones_creadas=[], total_clonadas=0, extra=1)


class TestModificarVigenciaRequest:
    def test_valid_with_filters(self):
        req = ModificarVigenciaRequest(
            materia_id=uuid.uuid4(),
            carrera_id=uuid.uuid4(),
            cohorte_id=uuid.uuid4(),
            desde=date(2026, 8, 1),
            hasta=date(2026, 12, 31),
        )
        assert req.desde == date(2026, 8, 1)

    def test_at_least_one_filter_required(self):
        with pytest.raises(ValidationError, match="al menos un filtro"):
            ModificarVigenciaRequest(
                desde=date(2026, 1, 1),
            )

    def test_only_materia_id_sufficient(self):
        req = ModificarVigenciaRequest(
            materia_id=uuid.uuid4(),
            desde=date(2026, 1, 1),
        )
        assert req.materia_id is not None

    def test_only_carrera_id_sufficient(self):
        req = ModificarVigenciaRequest(
            carrera_id=uuid.uuid4(),
        )
        assert req.carrera_id is not None

    def test_hasta_before_desde_fails(self):
        with pytest.raises(ValidationError, match="posterior o igual"):
            ModificarVigenciaRequest(
                materia_id=uuid.uuid4(),
                desde=date(2026, 12, 31),
                hasta=date(2026, 1, 1),
            )

    def test_only_desde_ok(self):
        req = ModificarVigenciaRequest(
            materia_id=uuid.uuid4(),
            desde=date(2026, 1, 1),
        )
        assert req.desde == date(2026, 1, 1)
        assert req.hasta is None

    def test_only_hasta_ok(self):
        req = ModificarVigenciaRequest(
            materia_id=uuid.uuid4(),
            hasta=date(2026, 12, 31),
        )
        assert req.hasta == date(2026, 12, 31)
        assert req.desde is None

    def test_extra_forbid(self):
        with pytest.raises(ValidationError, match="Extra inputs are not permitted"):
            ModificarVigenciaRequest(
                materia_id=uuid.uuid4(),
                extra=1,
            )


class TestModificarVigenciaResponse:
    def test_valid(self):
        resp = ModificarVigenciaResponse(
            asignaciones_actualizadas=5, total_encontradas=5,
        )
        assert resp.asignaciones_actualizadas == 5
        assert resp.total_encontradas == 5

    def test_extra_forbid(self):
        with pytest.raises(ValidationError, match="Extra inputs are not permitted"):
            ModificarVigenciaResponse(
                asignaciones_actualizadas=0, total_encontradas=0, extra=1,
            )


class TestExportarEquipoParams:
    def test_valid_with_filters(self):
        params = ExportarEquipoParams(
            materia_id=uuid.uuid4(),
            carrera_id=uuid.uuid4(),
            cohorte_id=uuid.uuid4(),
            vigente=True,
        )
        assert params.materia_id is not None

    def test_at_least_one_filter_required(self):
        with pytest.raises(ValidationError, match="al menos un filtro"):
            ExportarEquipoParams()

    def test_only_materia_id_sufficient(self):
        params = ExportarEquipoParams(materia_id=uuid.uuid4())
        assert params.materia_id is not None

    def test_only_carrera_id_sufficient(self):
        params = ExportarEquipoParams(carrera_id=uuid.uuid4())
        assert params.carrera_id is not None

    def test_only_cohorte_id_sufficient(self):
        params = ExportarEquipoParams(cohorte_id=uuid.uuid4())
        assert params.cohorte_id is not None

    def test_extra_forbid(self):
        with pytest.raises(ValidationError, match="Extra inputs are not permitted"):
            ExportarEquipoParams(materia_id=uuid.uuid4(), extra=1)


class TestBuscarUsuariosParams:
    def test_valid_with_query(self):
        params = BuscarUsuariosParams(q="gonzalez")
        assert params.q == "gonzalez"
        assert params.limite == 20
        assert params.roles is None

    def test_default_limite(self):
        params = BuscarUsuariosParams(q="a")
        assert params.limite == 20

    def test_custom_limite(self):
        params = BuscarUsuariosParams(q="a", limite=5)
        assert params.limite == 5

    def test_roles_optional(self):
        params = BuscarUsuariosParams(q="mar", roles="PROFESOR,TUTOR")
        assert params.roles == "PROFESOR,TUTOR"

    def test_extra_forbid(self):
        with pytest.raises(ValidationError, match="Extra inputs are not permitted"):
            BuscarUsuariosParams(q="test", extra=1)


class TestUsuarioAutocompletadoResponse:
    def test_valid(self):
        uid = uuid.uuid4()
        resp = UsuarioAutocompletadoResponse(
            id=uid,
            nombre="Maria",
            apellidos="Gonzalez",
            email="maria@test.com",
            legajo="L-001",
        )
        assert resp.nombre == "Maria"
        assert resp.apellidos == "Gonzalez"
        assert resp.legajo == "L-001"

    def test_legajo_can_be_none(self):
        resp = UsuarioAutocompletadoResponse(
            id=uuid.uuid4(),
            nombre="Juan",
            apellidos="Perez",
            email="juan@test.com",
            legajo=None,
        )
        assert resp.legajo is None

    def test_extra_forbid(self):
        with pytest.raises(ValidationError, match="Extra inputs are not permitted"):
            UsuarioAutocompletadoResponse(
                id=uuid.uuid4(),
                nombre="Juan",
                apellidos="Perez",
                email="juan@test.com",
                extra=1,
            )
