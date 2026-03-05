import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient
from fastapi import status


class TestHealth:

    @pytest.mark.asyncio
    async def test_app_health(self, client: TestClient):
        resp = client.get('/health')
        assert resp.status_code == status.HTTP_200_OK
