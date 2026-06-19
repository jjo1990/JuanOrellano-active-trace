import uuid

import pytest


@pytest.mark.needs_db
class TestLiquidacionApiSecurity:
    async def test_sin_token_retorna_401_liquidaciones(self, async_client):
        response = await async_client.get("/api/liquidaciones?cohorte_id=00000000-0000-0000-0000-000000000001&periodo=2026-06")
        assert response.status_code in (401, 403)

    async def test_sin_token_retorna_401_salarios(self, async_client):
        response = await async_client.get("/api/salarios/base")
        assert response.status_code in (401, 403)

    async def test_sin_token_retorna_401_facturas(self, async_client):
        response = await async_client.get("/api/facturas")
        assert response.status_code in (401, 403)

    async def test_sin_token_retorna_401_calcular(self, async_client):
        response = await async_client.post("/api/liquidaciones/calcular", json={
            "cohorte_id": "00000000-0000-0000-0000-000000000001",
            "periodo": "2026-06",
        })
        assert response.status_code in (401, 403)

    async def test_sin_token_retorna_401_cerrar(self, async_client):
        response = await async_client.post("/api/liquidaciones/cerrar", json={
            "cohorte_id": "00000000-0000-0000-0000-000000000001",
            "periodo": "2026-06",
        })
        assert response.status_code in (401, 403)

    async def test_sin_token_retorna_401_salario_base_create(self, async_client):
        response = await async_client.post("/api/salarios/base", json={
            "rol": "PROFESOR", "monto": 80000.00, "desde": "2026-01-01",
        })
        assert response.status_code in (401, 403)

    async def test_sin_token_retorna_401_factura_create(self, async_client):
        response = await async_client.post("/api/facturas", json={
            "usuario_id": "00000000-0000-0000-0000-000000000001",
            "periodo": "2026-06", "detalle": "Honorarios",
        })
        assert response.status_code in (401, 403)


@pytest.mark.needs_db
class TestLiquidacionApiRouteExists:
    """Verifica que los endpoints devuelvan 401/403 (no 404) — significa que las rutas existen."""

    async def test_liquidacion_endpoint_exists(self, async_client):
        response = await async_client.get("/api/liquidaciones?cohorte_id=00000000-0000-0000-0000-000000000001&periodo=2026-06")
        assert response.status_code in (401, 403)

    async def test_salario_base_endpoint_exists(self, async_client):
        response = await async_client.get("/api/salarios/base")
        assert response.status_code in (401, 403)

    async def test_salario_plus_endpoint_exists(self, async_client):
        response = await async_client.get("/api/salarios/plus")
        assert response.status_code in (401, 403)

    async def test_factura_endpoint_exists(self, async_client):
        response = await async_client.get("/api/facturas")
        assert response.status_code in (401, 403)
