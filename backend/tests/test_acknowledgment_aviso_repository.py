"""Tests para AcknowledgmentAvisoRepository (C-15)."""

import uuid
from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.acknowledgment_aviso import AcknowledgmentAviso
from app.models.aviso import Aviso
from app.models.user import User
from app.repositories.acknowledgment_aviso_repository import (
    AcknowledgmentAvisoRepository,
)


@pytest.fixture
async def seed_ack_repo(tenant_a, db_session: AsyncSession):
    tenant_id = tenant_a.id
    ahora = datetime.now(timezone.utc)

    user = User(
        email="ack_test@test.com",
        password_hash="hash",
        nombre="Ack",
        apellidos="Test",
        tenant_id=tenant_id,
    )
    db_session.add(user)
    await db_session.flush()

    aviso = Aviso(
        tenant_id=tenant_id,
        alcance="Global",
        severidad="Info",
        titulo="Aviso con ack",
        cuerpo="Requiere acuse",
        inicio_en=ahora - timedelta(days=1),
        fin_en=ahora + timedelta(days=5),
        orden=1,
        activo=True,
        requiere_ack=True,
    )
    db_session.add(aviso)
    await db_session.commit()
    await db_session.refresh(user)
    await db_session.refresh(aviso)

    return {
        "tenant_id": tenant_id,
        "usuario_id": user.id,
        "aviso_id": aviso.id,
    }


@pytest.mark.needs_db
class TestAcknowledgmentAvisoRepository:
    async def test_create_ack(self, seed_ack_repo, db_session):
        repo = AcknowledgmentAvisoRepository(
            db_session, seed_ack_repo["tenant_id"]
        )
        ack = AcknowledgmentAviso(
            aviso_id=seed_ack_repo["aviso_id"],
            usuario_id=seed_ack_repo["usuario_id"],
        )

        created = await repo.create(ack)
        assert created.id is not None
        assert created.aviso_id == seed_ack_repo["aviso_id"]
        assert created.usuario_id == seed_ack_repo["usuario_id"]
        assert created.confirmado_at is not None

    async def test_get_by_aviso_usuario_returns_ack(self, seed_ack_repo, db_session):
        repo = AcknowledgmentAvisoRepository(
            db_session, seed_ack_repo["tenant_id"]
        )
        ack = AcknowledgmentAviso(
            aviso_id=seed_ack_repo["aviso_id"],
            usuario_id=seed_ack_repo["usuario_id"],
        )
        await repo.create(ack)

        fetched = await repo.get_by_aviso_usuario(
            seed_ack_repo["aviso_id"], seed_ack_repo["usuario_id"]
        )
        assert fetched is not None
        assert fetched.aviso_id == seed_ack_repo["aviso_id"]

    async def test_get_by_aviso_usuario_returns_none(self, seed_ack_repo, db_session):
        repo = AcknowledgmentAvisoRepository(
            db_session, seed_ack_repo["tenant_id"]
        )
        fake_aviso_id = uuid.uuid4()
        result = await repo.get_by_aviso_usuario(
            fake_aviso_id, seed_ack_repo["usuario_id"]
        )
        assert result is None

    async def test_count_by_aviso_counts_acks(self, seed_ack_repo, db_session):
        repo = AcknowledgmentAvisoRepository(
            db_session, seed_ack_repo["tenant_id"]
        )
        ack1 = AcknowledgmentAviso(
            aviso_id=seed_ack_repo["aviso_id"],
            usuario_id=seed_ack_repo["usuario_id"],
        )
        await repo.create(ack1)

        user2 = User(
            email="ack_test2@test.com",
            password_hash="hash",
            nombre="Ack2",
            apellidos="Test",
            tenant_id=seed_ack_repo["tenant_id"],
        )
        db_session.add(user2)
        await db_session.commit()
        await db_session.refresh(user2)

        ack2 = AcknowledgmentAviso(
            aviso_id=seed_ack_repo["aviso_id"],
            usuario_id=user2.id,
        )
        await repo.create(ack2)

        count = await repo.count_by_aviso(seed_ack_repo["aviso_id"])
        assert count == 2

    async def test_count_by_aviso_returns_zero_for_no_acks(
        self, seed_ack_repo, db_session
    ):
        repo = AcknowledgmentAvisoRepository(
            db_session, seed_ack_repo["tenant_id"]
        )
        count = await repo.count_by_aviso(uuid.uuid4())
        assert count == 0

    async def test_count_by_aviso_only_counts_non_deleted(
        self, seed_ack_repo, db_session
    ):
        repo = AcknowledgmentAvisoRepository(
            db_session, seed_ack_repo["tenant_id"]
        )
        ack = AcknowledgmentAviso(
            aviso_id=seed_ack_repo["aviso_id"],
            usuario_id=seed_ack_repo["usuario_id"],
        )
        await repo.create(ack)

        ack.deleted_at = datetime.now(timezone.utc)
        db_session.add(ack)
        await db_session.commit()

        count = await repo.count_by_aviso(seed_ack_repo["aviso_id"])
        assert count == 0
