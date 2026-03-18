import pytest
from fastapi import status
from httpx import AsyncClient

from app.core.domain.permission_discovery import get_all_permissions
from app.identity.domain.value_objects import PermissionID
from app.identity.infra.models import PermissionModel


async def create_test_permissions(async_db_session):
    from sqlalchemy import select

    stmt = select(PermissionModel.codename)
    result = await async_db_session.execute(stmt)
    existing_codenames = {row.codename for row in result.all()}

    all_permissions = get_all_permissions()
    for perm_enum in all_permissions:
        codename = str(perm_enum)
        if codename in existing_codenames:
            continue

        permission_model = PermissionModel(
            id=str(PermissionID()),
            name=perm_enum.name.replace("_", " ").title(),
            codename=codename,
        )
        async_db_session.add(permission_model)

    await async_db_session.commit()


class TestPermissionList:

    @pytest.mark.asyncio
    async def test_list_permissions_success(self, admin_client: AsyncClient, async_db_session):
        await create_test_permissions(async_db_session)
        resp = await admin_client.get("/api/v1/permissions")
        assert resp.status_code == status.HTTP_200_OK
        data = resp.json()
        assert "items" in data
        assert "total" in data
        assert "limit" in data
        assert "offset" in data
        assert isinstance(data["items"], list)
        assert data["total"] >= 17

    @pytest.mark.asyncio
    async def test_list_permissions_with_pagination(self, admin_client: AsyncClient, async_db_session):
        await create_test_permissions(async_db_session)
        resp = await admin_client.get("/api/v1/permissions?limit=5&offset=0")
        assert resp.status_code == status.HTTP_200_OK
        data = resp.json()
        assert data["limit"] == 5
        assert data["offset"] == 0

    @pytest.mark.asyncio
    async def test_list_permissions_filter_by_name(
        self, admin_client: AsyncClient, test_permission, async_db_session
    ):
        await create_test_permissions(async_db_session)
        resp = await admin_client.get(f"/api/v1/permissions?name={test_permission.name}")
        assert resp.status_code == status.HTTP_200_OK
        data = resp.json()
        assert len(data["items"]) >= 1
        assert data["items"][0]["name"] == test_permission.name

    @pytest.mark.asyncio
    async def test_list_permissions_filter_by_codename(
        self, admin_client: AsyncClient, test_permission, async_db_session
    ):
        await create_test_permissions(async_db_session)
        resp = await admin_client.get(f"/api/v1/permissions?codename={test_permission.codename}")
        assert resp.status_code == status.HTTP_200_OK
        data = resp.json()
        assert len(data["items"]) >= 1
        assert data["items"][0]["codename"] == test_permission.codename

    @pytest.mark.asyncio
    async def test_list_permissions_unauthorized(self, client: AsyncClient, async_db_session):
        await create_test_permissions(async_db_session)
        resp = await client.get("/api/v1/permissions")
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED


class TestPermissionGet:

    @pytest.mark.asyncio
    async def test_get_permission_by_id(self, admin_client: AsyncClient, test_permission, async_db_session):
        await create_test_permissions(async_db_session)
        resp = await admin_client.get(f"/api/v1/permissions/{test_permission.id}")
        assert resp.status_code == status.HTTP_200_OK
        data = resp.json()
        assert data["id"] == str(test_permission.id)
        assert data["name"] == test_permission.name
        assert data["codename"] == test_permission.codename

    @pytest.mark.asyncio
    async def test_get_nonexistent_permission(self, admin_client: AsyncClient, async_db_session):
        await create_test_permissions(async_db_session)
        resp = await admin_client.get("/api/v1/permissions/00000000-0000-0000-0000-000000000000")
        assert resp.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.asyncio
    async def test_get_permission_by_codename(
        self, admin_client: AsyncClient, test_permission, async_db_session
    ):
        await create_test_permissions(async_db_session)
        resp = await admin_client.get(f"/api/v1/permissions/codename/{test_permission.codename}")
        assert resp.status_code == status.HTTP_200_OK
        data = resp.json()
        assert data["codename"] == test_permission.codename

    @pytest.mark.asyncio
    async def test_get_permission_by_nonexistent_codename(self, admin_client: AsyncClient, async_db_session):
        await create_test_permissions(async_db_session)
        resp = await admin_client.get("/api/v1/permissions/codename/nonexistent.codename")
        assert resp.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.asyncio
    async def test_get_permission_unauthorized(self, client: AsyncClient, test_permission, async_db_session):
        await create_test_permissions(async_db_session)
        resp = await client.get(f"/api/v1/permissions/{test_permission.id}")
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED


class TestPermissionAutoDiscovery:
    """Tests for permission auto-discovery."""

    # Expected minimum permission count: UserPermission(5) + GroupPermission(7) + PermissionPermission(5) = 17
    MIN_EXPECTED_PERMISSION_COUNT = 17

    @pytest.mark.asyncio
    async def test_permissions_exist_in_database(self, admin_client: AsyncClient, async_db_session):
        """Test that permissions were auto-discovered and created."""
        await create_test_permissions(async_db_session)
        resp = await admin_client.get("/api/v1/permissions")
        assert resp.status_code == status.HTTP_200_OK
        data = resp.json()
        assert data["total"] >= self.MIN_EXPECTED_PERMISSION_COUNT

    @pytest.mark.asyncio
    async def test_user_permissions_exist(self, admin_client: AsyncClient, async_db_session):
        await create_test_permissions(async_db_session)
        resp = await admin_client.get("/api/v1/permissions?codename=user.can_list")
        assert resp.status_code == status.HTTP_200_OK
        data = resp.json()
        assert len(data["items"]) >= 1
        assert data["items"][0]["codename"] == "user.can_list"

    @pytest.mark.asyncio
    async def test_group_permissions_exist(self, admin_client: AsyncClient, async_db_session):
        await create_test_permissions(async_db_session)
        resp = await admin_client.get("/api/v1/permissions?codename=group.can_list")
        assert resp.status_code == status.HTTP_200_OK
        data = resp.json()
        assert len(data["items"]) >= 1
        assert data["items"][0]["codename"] == "group.can_list"

    @pytest.mark.asyncio
    async def test_permission_permissions_exist(self, admin_client: AsyncClient, async_db_session):
        await create_test_permissions(async_db_session)
        resp = await admin_client.get("/api/v1/permissions?codename=permission.can_list")
        assert resp.status_code == status.HTTP_200_OK
        data = resp.json()
        assert len(data["items"]) >= 1
        assert data["items"][0]["codename"] == "permission.can_list"
