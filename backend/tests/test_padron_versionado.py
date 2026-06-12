"""Tests para PadronRepository — versionado de padrones (C-09)."""

import uuid
from datetime import date

import pytest
from sqlalchemy import select

from app.models.carrera import Carrera
from app.models.entrada_padron import EntradaPadron
from app.models.materia import Materia
from app.models.cohorte import Cohorte
from app.models.tenant import Tenant
from app.models.user import User
from app.models.version_padron import VersionPadron
from app.repositories.padron_repository import PadronRepository
from app.core.security import hash_password


@pytest.fixture
async def padron_fixtures(db_session, tenant_a):
    """Crea: carrera, materia, cohorte, user para tests de padrón."""
    carrera = Carrera(codigo="CARR001", nombre="Ingeniería", tenant_id=tenant_a.id)
    db_session.add(carrera)
    await db_session.flush()
    materia = Materia(codigo="MAT101", nombre="Matemáticas", tenant_id=tenant_a.id)
    db_session.add(materia)
    await db_session.flush()
    cohorte = Cohorte(
        carrera_id=carrera.id, nombre="2026-A", anio=2026,
        vig_desde=date(2026, 1, 1), tenant_id=tenant_a.id, activa=True,
    )
    db_session.add(cohorte)
    user = User(
        email="cargador@test.com", password_hash=hash_password("pass123!"),
        nombre="Cargador", apellidos="Test", tenant_id=tenant_a.id,
    )
    db_session.add(user)
    user_b = User(
        email="otro@test.com", password_hash=hash_password("pass123!"),
        nombre="Otro", apellidos="User", tenant_id=tenant_a.id,
    )
    db_session.add(user_b)
    await db_session.commit()
    await db_session.refresh(materia)
    await db_session.refresh(cohorte)
    await db_session.refresh(user)
    await db_session.refresh(user_b)
    return {
        "materia": materia,
        "cohorte": cohorte,
        "user": user,
        "user_b": user_b,
        "tenant": tenant_a,
    }


@pytest.mark.needs_db
class TestPadronVersionado:
    async def test_crear_version_con_activa_true(self, db_session, tenant_a, padron_fixtures):
        repo = PadronRepository(db_session, tenant_a.id)
        version = VersionPadron(
            materia_id=padron_fixtures["materia"].id,
            cohorte_id=padron_fixtures["cohorte"].id,
            cargado_por=padron_fixtures["user"].id,
            activa=True,
        )
        result = await repo.create_version(version)
        await db_session.commit()
        assert result.id is not None
        assert result.activa is True
        assert result.tenant_id == tenant_a.id

    async def test_activar_nueva_version_desactiva_anterior(self, db_session, tenant_a, padron_fixtures):
        repo = PadronRepository(db_session, tenant_a.id)
        v1 = VersionPadron(
            materia_id=padron_fixtures["materia"].id,
            cohorte_id=padron_fixtures["cohorte"].id,
            cargado_por=padron_fixtures["user"].id,
            activa=True,
        )
        await repo.create_version(v1)
        await db_session.flush()

        v2 = VersionPadron(
            materia_id=padron_fixtures["materia"].id,
            cohorte_id=padron_fixtures["cohorte"].id,
            cargado_por=padron_fixtures["user_b"].id,
            activa=True,
        )
        result = await repo.create_version(v2)
        await db_session.commit()

        assert result.activa is True
        assert v1.activa is False

    async def test_activar_version_tenant_a_no_afecta_tenant_b(self, db_session, tenant_a, tenant_b, padron_fixtures):
        repo_a = PadronRepository(db_session, tenant_a.id)
        repo_b = PadronRepository(db_session, tenant_b.id)

        v_a = VersionPadron(
            materia_id=padron_fixtures["materia"].id,
            cohorte_id=padron_fixtures["cohorte"].id,
            cargado_por=padron_fixtures["user"].id,
            activa=True,
        )
        v_b = VersionPadron(
            materia_id=padron_fixtures["materia"].id,
            cohorte_id=padron_fixtures["cohorte"].id,
            cargado_por=padron_fixtures["user"].id,
            activa=True,
        )
        await repo_a.create_version(v_a)
        await repo_b.create_version(v_b)
        await db_session.flush()

        v2_a = VersionPadron(
            materia_id=padron_fixtures["materia"].id,
            cohorte_id=padron_fixtures["cohorte"].id,
            cargado_por=padron_fixtures["user"].id,
            activa=True,
        )
        await repo_a.create_version(v2_a)
        await db_session.commit()

        active_b = await repo_b.get_active_version(
            padron_fixtures["materia"].id, padron_fixtures["cohorte"].id,
        )
        assert active_b is not None
        assert active_b.activa is True

    async def test_crear_entrada_asociada_a_version(self, db_session, tenant_a, padron_fixtures):
        repo = PadronRepository(db_session, tenant_a.id)
        version = VersionPadron(
            materia_id=padron_fixtures["materia"].id,
            cohorte_id=padron_fixtures["cohorte"].id,
            cargado_por=padron_fixtures["user"].id,
            activa=True,
        )
        await repo.create_version(version)
        await db_session.flush()

        entrada = EntradaPadron(
            version_id=version.id,
            nombre="Juan",
            apellidos="Pérez",
            comision="A",
            regional="BS AS",
        )
        result = await repo.create_entrada(entrada)
        await db_session.commit()
        assert result.id is not None
        assert result.nombre == "Juan"
        assert result.version_id == version.id
        assert result.tenant_id == tenant_a.id

    async def test_entrada_con_usuario_id_none(self, db_session, tenant_a, padron_fixtures):
        repo = PadronRepository(db_session, tenant_a.id)
        version = VersionPadron(
            materia_id=padron_fixtures["materia"].id,
            cohorte_id=padron_fixtures["cohorte"].id,
            cargado_por=padron_fixtures["user"].id,
            activa=True,
        )
        await repo.create_version(version)
        await db_session.flush()

        entrada = EntradaPadron(
            version_id=version.id,
            nombre="Sin",
            apellidos="Cuenta",
            usuario_id=None,
            comision="B",
        )
        result = await repo.create_entrada(entrada)
        await db_session.commit()
        assert result.usuario_id is None

    async def test_entrada_con_usuario_id_valido(self, db_session, tenant_a, padron_fixtures):
        repo = PadronRepository(db_session, tenant_a.id)
        version = VersionPadron(
            materia_id=padron_fixtures["materia"].id,
            cohorte_id=padron_fixtures["cohorte"].id,
            cargado_por=padron_fixtures["user"].id,
            activa=True,
        )
        await repo.create_version(version)
        await db_session.flush()

        entrada = EntradaPadron(
            version_id=version.id,
            nombre="Con",
            apellidos="Usuario",
            usuario_id=padron_fixtures["user"].id,
            comision="C",
        )
        result = await repo.create_entrada(entrada)
        await db_session.commit()
        assert result.usuario_id == padron_fixtures["user"].id

    async def test_get_version_retorna_none_si_no_existe(self, db_session, tenant_a):
        repo = PadronRepository(db_session, tenant_a.id)
        result = await repo.get_version(uuid.uuid4())
        assert result is None

    async def test_list_versions_filtra_por_materia(self, db_session, tenant_a, padron_fixtures):
        repo = PadronRepository(db_session, tenant_a.id)
        v1 = VersionPadron(
            materia_id=padron_fixtures["materia"].id,
            cohorte_id=padron_fixtures["cohorte"].id,
            cargado_por=padron_fixtures["user"].id,
            activa=True,
        )
        await repo.create_version(v1)
        await db_session.commit()

        versions = await repo.list_versions(materia_id=padron_fixtures["materia"].id)
        assert len(versions) == 1

    async def test_list_entradas_por_version(self, db_session, tenant_a, padron_fixtures):
        repo = PadronRepository(db_session, tenant_a.id)
        version = VersionPadron(
            materia_id=padron_fixtures["materia"].id,
            cohorte_id=padron_fixtures["cohorte"].id,
            cargado_por=padron_fixtures["user"].id,
            activa=True,
        )
        await repo.create_version(version)
        await db_session.flush()

        for i in range(3):
            e = EntradaPadron(
                version_id=version.id, nombre=f"Alumno{i}",
                apellidos="Test", comision="A",
            )
            await repo.create_entrada(e)
        await db_session.commit()

        entradas = await repo.list_entradas(version.id)
        assert len(entradas) == 3

    async def test_count_entradas(self, db_session, tenant_a, padron_fixtures):
        repo = PadronRepository(db_session, tenant_a.id)
        version = VersionPadron(
            materia_id=padron_fixtures["materia"].id,
            cohorte_id=padron_fixtures["cohorte"].id,
            cargado_por=padron_fixtures["user"].id,
            activa=True,
        )
        await repo.create_version(version)
        await db_session.flush()

        for i in range(5):
            e = EntradaPadron(
                version_id=version.id, nombre=f"Al{i}",
                apellidos="Test", comision="A",
            )
            await repo.create_entrada(e)
        await db_session.commit()

        count = await repo.count_entradas(version.id)
        assert count == 5

    async def test_soft_delete_by_materia(self, db_session, tenant_a, padron_fixtures):
        repo = PadronRepository(db_session, tenant_a.id)
        version = VersionPadron(
            materia_id=padron_fixtures["materia"].id,
            cohorte_id=padron_fixtures["cohorte"].id,
            cargado_por=padron_fixtures["user"].id,
            activa=True,
        )
        await repo.create_version(version)
        await db_session.flush()

        for i in range(2):
            e = EntradaPadron(
                version_id=version.id, nombre=f"Al{i}",
                apellidos="Test", comision="A",
            )
            await repo.create_entrada(e)
        await db_session.commit()

        filas = await repo.soft_delete_by_materia(padron_fixtures["materia"].id)
        await db_session.commit()
        assert filas > 0

        versions = await repo.list_versions(materia_id=padron_fixtures["materia"].id)
        assert len(versions) == 0

    async def test_get_active_version_retorna_none_si_no_hay(self, db_session, tenant_a, padron_fixtures):
        repo = PadronRepository(db_session, tenant_a.id)
        result = await repo.get_active_version(
            padron_fixtures["materia"].id, padron_fixtures["cohorte"].id,
        )
        assert result is None

    async def test_entrada_con_email_cifrado(self, db_session, tenant_a, padron_fixtures):
        repo = PadronRepository(db_session, tenant_a.id)
        version = VersionPadron(
            materia_id=padron_fixtures["materia"].id,
            cohorte_id=padron_fixtures["cohorte"].id,
            cargado_por=padron_fixtures["user"].id,
            activa=True,
        )
        await repo.create_version(version)
        await db_session.flush()

        entrada = EntradaPadron(
            version_id=version.id,
            nombre="Email",
            apellidos="Test",
            email="alumno@test.com",
        )
        await repo.create_entrada(entrada)
        await db_session.commit()

        assert entrada.email_encrypted is not None
        assert entrada.email_encrypted != "alumno@test.com"
        assert entrada.email == "alumno@test.com"

    async def test_list_versions_sin_materia_retorna_todas(self, db_session, tenant_a, padron_fixtures):
        repo = PadronRepository(db_session, tenant_a.id)
        v1 = VersionPadron(
            materia_id=padron_fixtures["materia"].id,
            cohorte_id=padron_fixtures["cohorte"].id,
            cargado_por=padron_fixtures["user"].id,
            activa=True,
        )
        await repo.create_version(v1)
        await db_session.commit()

        all_v = await repo.list_versions()
        assert len(all_v) >= 1

    async def test_batch_create_entradas(self, db_session, tenant_a, padron_fixtures):
        repo = PadronRepository(db_session, tenant_a.id)
        version = VersionPadron(
            materia_id=padron_fixtures["materia"].id,
            cohorte_id=padron_fixtures["cohorte"].id,
            cargado_por=padron_fixtures["user"].id,
            activa=True,
        )
        await repo.create_version(version)
        await db_session.flush()

        entradas = [
            EntradaPadron(version_id=version.id, nombre=f"Al{i}", apellidos="Test")
            for i in range(5)
        ]
        await repo.create_entradas_batch(entradas)
        await db_session.commit()

        all_e = await repo.list_entradas(version.id)
        assert len(all_e) == 5

    async def test_soft_delete_by_materia_rowcount(self, db_session, tenant_a, padron_fixtures):
        repo = PadronRepository(db_session, tenant_a.id)
        v1 = VersionPadron(
            materia_id=padron_fixtures["materia"].id,
            cohorte_id=padron_fixtures["cohorte"].id,
            cargado_por=padron_fixtures["user"].id,
            activa=True,
        )
        await repo.create_version(v1)
        await db_session.flush()

        for i in range(3):
            e = EntradaPadron(version_id=v1.id, nombre=f"Al{i}", apellidos="Test")
            await repo.create_entrada(e)
        await db_session.flush()

        filas = await repo.soft_delete_by_materia(padron_fixtures["materia"].id)
        await db_session.commit()
        # 1 version + 3 entradas = 4
        assert filas == 4
