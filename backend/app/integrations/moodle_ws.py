import logging

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from app.core.config import Settings

logger = logging.getLogger(__name__)


class MoodleWSException(Exception):
    """Error específico de Moodle Web Service."""


class MoodleClient:
    """Cliente HTTP para Moodle Web Services."""

    def __init__(self, base_url: str, token: str) -> None:
        self._base_url = base_url.rstrip("/")
        self._token = token
        settings = Settings()
        self._timeout = settings.moodle_ws_timeout

    async def _call(self, wsfunction: str, **kwargs) -> dict | list:
        params = {
            "wstoken": self._token,
            "wsfunction": wsfunction,
            "moodlewsrestformat": "json",
            **kwargs,
        }
        async with httpx.AsyncClient(timeout=self._timeout) as client:
            response = await client.get(self._base_url + "/webservice/rest/server.php", params=params)
        if response.status_code == 401:
            raise MoodleWSException("Autenticación fallida contra Moodle WS (HTTP 401).")
        response.raise_for_status()
        data = response.json()
        if isinstance(data, dict) and "exception" in data:
            raise MoodleWSException(f"Moodle WS error: {data.get('message', str(data))}")
        return data

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=15),
        retry=retry_if_exception_type((MoodleWSException, httpx.TimeoutException, httpx.HTTPStatusError, httpx.RequestError)),
    )
    async def get_enrolled_users(self, course_id: str | int) -> list[dict]:
        data = await self._call("core_enrol_get_enrolled_users", courseid=course_id)
        return [
            {
                "id": u.get("id"),
                "nombre": u.get("firstname", ""),
                "apellidos": u.get("lastname", ""),
                "email": u.get("email", ""),
            }
            for u in (data if isinstance(data, list) else [])
        ]

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=15),
        retry=retry_if_exception_type((MoodleWSException, httpx.TimeoutException, httpx.HTTPStatusError, httpx.RequestError)),
    )
    async def get_activities(self, course_id: str | int) -> list[dict]:
        data = await self._call("core_course_get_contents", courseid=course_id)
        if not isinstance(data, list):
            return []
        activities = []
        for section in data:
            for module in section.get("modules", []):
                activities.append({
                    "id": module.get("id"),
                    "name": module.get("name"),
                    "modname": module.get("modname"),
                })
        return activities

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=15),
        retry=retry_if_exception_type((MoodleWSException, httpx.TimeoutException, httpx.HTTPStatusError, httpx.RequestError)),
    )
    async def get_grades(self, course_id: str | int) -> list[dict]:
        data = await self._call("gradereport_user_get_grade_items", courseid=course_id)
        if not isinstance(data, dict):
            return []
        items = data.get("usergrades", [])
        return list(items) if isinstance(items, list) else []
