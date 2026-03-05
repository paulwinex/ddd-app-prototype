import pytest
from httpx import AsyncClient
from fastapi import status


class TestAdminUser:

    @pytest.mark.asyncio
    async def test_app_health(self, admin_client: AsyncClient):
        resp = await admin_client.get('/api/v1/auth/me')
        assert resp.status_code == status.HTTP_200_OK
        data = resp.json()
        assert data.get('id') is not None
        assert data.get('first_name') == "Super"
        assert data.get('last_name') == "Admin"
