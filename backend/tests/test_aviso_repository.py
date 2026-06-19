"""Tests para AvisoRepository (C-15)."""

import uuid
from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.aviso import Aviso
from app.models.materia import Materia
from app.repositories.aviso_repository import AvisoRepository


@pytest.fixture
async def seed_aviso_repo(tenant_a, db_session: AsyncSession):
    tenant_id = tenant_a.id
    ahora = datetime.now(timezone.utc)

    materia = Materia(codigo="MAT_AVISO", nombre="Materia para Avisos", activa=True, tenant_id=tenant_id)
    db_session.add(materia)
    await db_session.flush()

    aviso_global = Aviso(
        tenant_id=tenant_id,
        alcance="Global",
        severidad="Info",
        titulo="Aviso Global Activo",
        cuerpo="Contenido global",
        inicio_en=ahora - timedelta(days=1),
        fin_en=ahora + timedelta(days=5),
        orden=1,
        activo=True,
        requiere_ack=False,
    )

    aviso_global_vencido = Aviso(
        tenant_id=tenant_id,
        alcance="Global",
        severidad="Critico",
        titulo="Aviso Global Vencido",
        cuerpo="Ya venció",
        inicio_en=ahora - timedelta(days=30),
        fin_en=ahora - timedelta(days=1),
        orden=2,
        activo=True,
        requiere_ack=True,
    )

    aviso_materia = Aviso(
        tenant_id=tenant_id,
        alcance="PorMateria",
        materia_id=materia.id,
        severidad="Advertencia",
        titulo="Aviso por Materia",
        cuerpo="Contenido materia",
        inicio_en=ahora - timedelta(days=2),
        fin_en=ahora + timedelta(days=10),
        orden=0,
        activo=True,
        requiere_ack=True,
    )

    aviso_inactivo = Aviso(
        tenant_id=tenant_id,
        alcance="Global",
        severidad="Info",
        titulo="Aviso Inactivo",
        cuerpo="Inactivo",
        inicio_en=ahora - timedelta(days=1),
        fin_en=ahora + timedelta(days=5),
        orden=3,
        activo=False,
        requiere_ack=False,
    )

    soft_deleted = Aviso(
        tenant_id=tenant_id,
        alcance="Global",
        severidad="Info",
        titulo="Aviso Borrado",
        cuerpo="Borrado",
        inicio_en=ahora - timedelta(days=1),
        fin_en=ahora + timedelta(days=5),
        orden=4,
        activo=True,
        requiere_ack=False,
        deleted_at=ahora,
    )

    avisos = [aviso_global, aviso_global_vencido, aviso_materia, aviso_inactivo, soft_deleted]
    db_session.add_all(avisos)
    await db_session.commit()
    for a in avisos:
        await db_session.refresh(a)

    return {
        "tenant_id": tenant_id,
        "aviso_global_id": aviso_global.id,
        "aviso_global_vencido_id": aviso_global_vencido.id,
        "aviso_materia_id": aviso_materia.id,
        "aviso_inactivo_id": aviso_inactivo.id,
        "soft_deleted_id": soft_deleted.id,
        "materia_id": materia.id,
    }


@pytest.mark.needs_db
class TestAvisoRepository:
    async def test_create_aviso(self, tenant_a, db_session):
        repo = AvisoRepository(db_session, tenant_a.id)
        ahora = datetime.now(timezone.utc)

        aviso = Aviso(
            alcance="Global",
            severidad="Critico",
            titulo="Nuevo Aviso",
            cuerpo="Cuerpo nuevo",
            inicio_en=ahora,
            fin_en=ahora + timedelta(days=7),
            orden=1,
            activo=True,
            requiere_ack=True,
        )

        created = await repo.create(aviso)
        assert created.id is not None
        assert created.tenant_id == tenant_a.id
        assert created.alcance == "Global"
        assert created.titulo == "Nuevo Aviso"

    async def test_list_activos_en_ventana_returns_active_and_in_window(
        self, seed_aviso_repo, db_session
    ):
        repo = AvisoRepository(db_session, seed_aviso_repo["tenant_id"])
        results = await repo.list_activos_en_ventana(seed_aviso_repo["tenant_id"])

        titulos = {r.titulo for r in results}
        assert "Aviso Global Activo" in titulos
        assert "Aviso por Materia" in titulos
        assert "Aviso Global Vencido" not in titulos
        assert "Aviso Inactivo" not in titulos
        assert "Aviso Borrado" not in titulos

    async def test_list_by_alcance_filters_correctly(self, seed_aviso_repo, db_session):
        repo = AvisoRepository(db_session, seed_aviso_repo["tenant_id"])
        results = await repo.list_by_alcance(seed_aviso_repo["tenant_id"], "PorMateria")

        assert len(results) == 1
        assert results[0].titulo == "Aviso por Materia"

    async def test_list_by_alcance_includes_global(self, seed_aviso_repo, db_session):
        repo = AvisoRepository(db_session, seed_aviso_repo["tenant_id"])
        results = await repo.list_by_alcance(seed_aviso_repo["tenant_id"], "Global")

        # active + inactive + vencido — soft deleted excluded
        titulos = {r.titulo for r in results}
        assert len(results) == 3
        assert "Aviso Global Activo" in titulos
        assert "Aviso Global Vencido" in titulos
        assert "Aviso Inactivo" in titulos
        assert "Aviso Borrado" not in titulos

    async def test_soft_delete_marks_deleted_at(self, seed_aviso_repo, db_session):
        repo = AvisoRepository(db_session, seed_aviso_repo["tenant_id"])
        aviso_id = seed_aviso_repo["aviso_global_id"]

        await repo.soft_delete(aviso_id)

        deleted = await repo.get(aviso_id)
        assert deleted is None

    async def test_soft_delete_nonexistent_raises(self, tenant_a, db_session):
        repo = AvisoRepository(db_session, tenant_a.id)
        fake_id = uuid.uuid4()

        with pytest.raises(Exception):
            await repo.soft_delete(fake_id)

    async def test_list_activos_en_ventana_respects_tenant_isolation(
        self, seed_aviso_repo, tenant_b, db_session
    ):
        repo_b = AvisoRepository(db_session, tenant_b.id)
        results = await repo_b.list_activos_en_ventana(tenant_b.id)

        assert len(results) == 0
