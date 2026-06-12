"""Tests para MoodleClient (C-09)."""

import pytest
import httpx
from tenacity import RetryError
from unittest.mock import AsyncMock, patch

from app.integrations.moodle_ws import MoodleClient, MoodleWSException


@pytest.fixture
def moodle_client():
    return MoodleClient(base_url="https://moodle.example.com", token="test-token-123")


@pytest.mark.needs_db
class TestMoodleClient:

    async def test_get_enrolled_users_returns_mapped_list(self, moodle_client):
        mock_response_data = [
            {"id": 1, "firstname": "Juan", "lastname": "Perez", "email": "juan@test.com"},
            {"id": 2, "firstname": "Maria", "lastname": "Gomez", "email": "maria@test.com"},
        ]
        with patch.object(moodle_client, "_call", new=AsyncMock(return_value=mock_response_data)):
            result = await moodle_client.get_enrolled_users(course_id=10)
        assert len(result) == 2
        assert result[0]["nombre"] == "Juan"
        assert result[0]["apellidos"] == "Perez"
        assert result[0]["email"] == "juan@test.com"

    async def test_get_enrolled_users_empty_list(self, moodle_client):
        with patch.object(moodle_client, "_call", new=AsyncMock(return_value=[])):
            result = await moodle_client.get_enrolled_users(course_id=99)
        assert result == []

    async def test_moodle_ws_timeout_raises_exception(self, moodle_client):
        with patch.object(moodle_client, "_call", new=AsyncMock(side_effect=httpx.TimeoutException("timeout"))):
            with pytest.raises((MoodleWSException, RetryError)):
                await moodle_client.get_enrolled_users(course_id=1)

    async def test_moodle_ws_http_401_raises_exception(self, moodle_client):
        with patch.object(moodle_client, "_call", new=AsyncMock(side_effect=MoodleWSException("Autenticación fallida contra Moodle WS (HTTP 401)."))):
            with pytest.raises((MoodleWSException, RetryError)):
                await moodle_client.get_enrolled_users(course_id=1)

    async def test_moodle_ws_http_500_maps_to_error(self, moodle_client):
        with patch.object(moodle_client, "_call", new=AsyncMock(side_effect=MoodleWSException("Error HTTP en Moodle WS: 500"))):
            with pytest.raises((MoodleWSException, RetryError)):
                await moodle_client.get_enrolled_users(course_id=1)

    async def test_get_activities_returns_flat_list(self, moodle_client):
        mock_data = [
            {
                "id": 1, "name": "Section 1",
                "modules": [
                    {"id": 10, "name": "Quiz 1", "modname": "quiz"},
                    {"id": 11, "name": "Foro 1", "modname": "forum"},
                ],
            },
        ]
        with patch.object(moodle_client, "_call", new=AsyncMock(return_value=mock_data)):
            result = await moodle_client.get_activities(course_id=5)
        assert len(result) == 2
        assert result[0]["modname"] == "quiz"

    async def test_get_grades_returns_user_grades(self, moodle_client):
        mock_data = {"usergrades": [{"userid": 1, "grade": 85}, {"userid": 2, "grade": 92}]}
        with patch.object(moodle_client, "_call", new=AsyncMock(return_value=mock_data)):
            result = await moodle_client.get_grades(course_id=5)
        assert len(result) == 2
