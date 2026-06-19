import uuid

import pytest

from app.models.factura import EstadoFactura, Factura
from app.models.user import User
from app.schemas.factura import FacturaCreate, FacturaUpdate
from app.services.factura_service import FacturaService


@pytest.fixture
async def seed_factura_service(db_session, tenant_a):
    user_f = User(
        email="fs_fact@test.com", password_hash="hash",
        nombre="Facturante", apellidos="Test", tenant_id=tenant_a.id,
        legajo="L-FS", cbu_encrypted="enc_cbu", facturador=True,
    )
    user_no = User(
        email="fs_nofact@test.com", password_hash="hash",
        nombre="No", apellidos="Facturante", tenant_id=tenant_a.id,
        legajo="L-FS-NO", facturador=False,
    )
    db_session.add_all([user_f, user_no])
    await db_session.commit()

    return {
        "tenant_a_id": tenant_a.id,
        "user_f_id": user_f.id,
        "user_no_id": user_no.id,
    }


@pytest.mark.needs_db
class TestFacturaService:
    async def test_create_factura_success(self, db_session, seed_factura_service):
        d = seed_factura_service
        svc = FacturaService(db_session, d["tenant_a_id"])
        data = FacturaCreate(
            usuario_id=d["user_f_id"], periodo="2026-06",
            detalle="Honorarios junio",
        )
        result = await svc.create(data, d["user_f_id"])
        assert result.estado == "Pendiente"
        assert result.usuario_id == d["user_f_id"]

    async def test_create_factura_no_facturante_rejected(self, db_session, seed_factura_service):
        d = seed_factura_service
        svc = FacturaService(db_session, d["tenant_a_id"])
        data = FacturaCreate(
            usuario_id=d["user_no_id"], periodo="2026-06",
            detalle="Honorarios",
        )
        from fastapi import HTTPException
        with pytest.raises(HTTPException) as exc:
            await svc.create(data, d["user_f_id"])
        assert exc.value.status_code == 422

    async def test_abonar_factura(self, db_session, seed_factura_service):
        d = seed_factura_service
        svc = FacturaService(db_session, d["tenant_a_id"])
        data = FacturaCreate(
            usuario_id=d["user_f_id"], periodo="2026-06",
            detalle="Honorarios junio",
        )
        created = await svc.create(data, d["user_f_id"])
        svc2 = FacturaService(db_session, d["tenant_a_id"])
        result = await svc2.abonar(created.id, d["user_f_id"])
        assert result.estado == "Abonada"
        assert result.abonada_at is not None

    async def test_abonar_factura_ya_abonada_rejected(self, db_session, seed_factura_service):
        d = seed_factura_service
        svc = FacturaService(db_session, d["tenant_a_id"])
        data = FacturaCreate(
            usuario_id=d["user_f_id"], periodo="2026-06",
            detalle="Honorarios",
        )
        created = await svc.create(data, d["user_f_id"])
        svc2 = FacturaService(db_session, d["tenant_a_id"])
        await svc2.abonar(created.id, d["user_f_id"])
        from fastapi import HTTPException
        svc3 = FacturaService(db_session, d["tenant_a_id"])
        with pytest.raises(HTTPException) as exc:
            await svc3.abonar(created.id, d["user_f_id"])
        assert exc.value.status_code == 422

    async def test_marcar_pendiente(self, db_session, seed_factura_service):
        d = seed_factura_service
        svc = FacturaService(db_session, d["tenant_a_id"])
        data = FacturaCreate(
            usuario_id=d["user_f_id"], periodo="2026-06",
            detalle="Honorarios",
        )
        created = await svc.create(data, d["user_f_id"])
        svc2 = FacturaService(db_session, d["tenant_a_id"])
        await svc2.abonar(created.id, d["user_f_id"])
        svc3 = FacturaService(db_session, d["tenant_a_id"])
        result = await svc3.marcar_pendiente(created.id, d["user_f_id"])
        assert result.estado == "Pendiente"
        assert result.abonada_at is None

    async def test_update_factura(self, db_session, seed_factura_service):
        d = seed_factura_service
        svc = FacturaService(db_session, d["tenant_a_id"])
        data = FacturaCreate(
            usuario_id=d["user_f_id"], periodo="2026-06",
            detalle="Honorarios",
        )
        created = await svc.create(data, d["user_f_id"])
        svc2 = FacturaService(db_session, d["tenant_a_id"])
        update = FacturaUpdate(detalle="Honorarios actualizados")
        result = await svc2.update(created.id, update)
        assert "actualizados" in result.detalle

    async def test_list_with_filters(self, db_session, seed_factura_service):
        d = seed_factura_service
        svc = FacturaService(db_session, d["tenant_a_id"])
        data1 = FacturaCreate(usuario_id=d["user_f_id"], periodo="2026-06", detalle="Junio")
        data2 = FacturaCreate(usuario_id=d["user_f_id"], periodo="2026-07", detalle="Julio")
        await svc.create(data1, d["user_f_id"])
        await svc.create(data2, d["user_f_id"])
        results = await svc.list_with_filters(periodo="2026-06")
        assert len(results) == 1
        assert results[0].periodo == "2026-06"
