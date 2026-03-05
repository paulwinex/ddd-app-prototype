import pytest
from fastapi.testclient import TestClient
from fastapi import status

from app.core.settings import Settings


class TestAdminUser:

    @pytest.mark.asyncio
    async def test_app_health(self, admin_client: TestClient, test_settings: Settings):
        resp = admin_client.get('/api/v1/auth/me')
        assert resp.status_code == status.HTTP_200_OK
        data = resp.json()
        assert data.get('id') is not None
        assert data.get('first_name') == "Super"
        assert data.get('last_name') == "Admin"
