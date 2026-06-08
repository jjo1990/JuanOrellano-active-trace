"""RED → GREEN: App startup / instantiation.

Task 5.4–5.5 — Strict TDD.
"""
import pytest
from asgi_lifespan import LifespanManager


class TestAppStartup:
    def test_app_instantiates(self):
        from app.main import create_app

        app = create_app()
        assert app.title == "activia-trace"
        assert app.version == "0.1.0"

    @pytest.mark.asyncio
    async def test_app_lifespan_starts_without_error(self):
        from app.main import create_app

        app = create_app()
        async with LifespanManager(app):
            assert hasattr(app.state, "engine")
            assert app.state.engine is not None
