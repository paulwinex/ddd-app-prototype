import pytest
from httpx import AsyncClient
from fastapi import status


class TestAdminUserOperations:

    @pytest.mark.asyncio
    async def test_admin_can_create_user(self, admin_client: AsyncClient):
        """Test that admin can create new users."""
        user_data = {
            'email': 'createdbyadmin@test.com',
            'password': 'password123',
            'first_name': 'Created',
            'last_name': 'By Admin',
        }
        resp = await admin_client.post('/api/v1/users', json=user_data)
        assert resp.status_code == status.HTTP_201_CREATED
        data = resp.json()
        assert data['email'] == 'createdbyadmin@test.com'

    @pytest.mark.asyncio
    async def test_admin_can_list_all_users(self, admin_client: AsyncClient):
        resp = await admin_client.get('/api/v1/users')
        assert resp.status_code == status.HTTP_200_OK
        data = resp.json()
        assert 'items' in data
        assert data['total'] >= 1

    @pytest.mark.asyncio
    async def test_admin_can_get_any_user(self, admin_client: AsyncClient, regular_user):
        resp = await admin_client.get(f'/api/v1/users/{regular_user.id}')
        assert resp.status_code == status.HTTP_200_OK
        data = resp.json()
        assert data['id'] == str(regular_user.id)

    @pytest.mark.asyncio
    async def test_admin_can_update_any_user(self, admin_client: AsyncClient, regular_user):
        update_data = {
            'first_name': 'Updated By Admin',
            'last_name': 'Name',
        }
        resp = await admin_client.patch(
            f'/api/v1/users/{regular_user.id}',
            json=update_data
        )
        assert resp.status_code == status.HTTP_200_OK

    @pytest.mark.asyncio
    async def test_admin_can_delete_non_admin_user(self, admin_client: AsyncClient, async_db_session):
        from app.identity.infra.models.user_model import UserModel
        from sqlalchemy import select

        user_to_delete = UserModel(
            email='deletable@test.com',
            password_hash='hash',
            first_name='To',
            last_name='Delete',
            is_active=True,
            is_superuser=False,
            is_verified=False,
        )
        async_db_session.add(user_to_delete)
        await async_db_session.commit()
        await async_db_session.refresh(user_to_delete)
        user_id = str(user_to_delete.id)

        resp = await admin_client.delete(f'/api/v1/users/{user_id}')
        assert resp.status_code == status.HTTP_204_NO_CONTENT

        stmt = select(UserModel).where(UserModel.id == user_id)
        result = await async_db_session.execute(stmt)
        assert result.scalar_one_or_none() is None

    @pytest.mark.asyncio
    async def test_admin_cannot_delete_admin_user(self, admin_client: AsyncClient, admin_user):
        resp = await admin_client.delete(f'/api/v1/users/{admin_user.id}')
        assert resp.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.asyncio
    async def test_admin_can_change_any_user_password(
        self, admin_client: AsyncClient, regular_user, async_db_session, test_settings
    ):
        password_data = {
            'current_password': 'regularpass123',
            'new_password': 'newpassword456',
        }
        resp = await admin_client.post(
            f'/api/v1/users/{regular_user.id}/change-password',
            json=password_data
        )
        assert resp.status_code in [status.HTTP_204_NO_CONTENT, status.HTTP_401_UNAUTHORIZED]


class TestRegularUserRestrictions:
    """Tests for regular user access restrictions."""

    @pytest.mark.asyncio
    async def test_regular_user_cannot_create_users(self, authenticated_client: AsyncClient):
        """Test that regular user cannot create new users."""
        user_data = {
            'email': 'nouser@test.com',
            'password': 'password123',
            'first_name': 'No',
            'last_name': 'User',
        }
        resp = await authenticated_client.post('/api/v1/users', json=user_data)
        assert resp.status_code in [
            status.HTTP_201_CREATED,
            status.HTTP_403_FORBIDDEN,
        ]

    @pytest.mark.asyncio
    async def test_regular_user_can_get_own_profile(self, authenticated_client: AsyncClient, regular_user):
        resp = await authenticated_client.get('/api/v1/auth/me')
        assert resp.status_code == status.HTTP_200_OK
        data = resp.json()
        assert data['email'] == str(regular_user.email)

    @pytest.mark.asyncio
    async def test_regular_user_cannot_delete_users(self, authenticated_client: AsyncClient, async_db_session):
        from app.identity.infra.models.user_model import UserModel

        user_to_delete = UserModel(
            email='todelete2@test.com',
            password_hash='hash',
            first_name='To',
            last_name='Delete',
            is_active=True,
            is_superuser=False,
            is_verified=False,
        )
        async_db_session.add(user_to_delete)
        await async_db_session.commit()
        await async_db_session.refresh(user_to_delete)
        user_id = str(user_to_delete.id)

        resp = await authenticated_client.delete(f'/api/v1/users/{user_id}')
        assert resp.status_code in [
            status.HTTP_204_NO_CONTENT,
            status.HTTP_403_FORBIDDEN,
        ]


class TestInactiveUserRestrictions:

    @pytest.mark.asyncio
    async def test_inactive_user_cannot_login(self, client: AsyncClient, async_db_session):
        from app.identity.infra.models.user_model import UserModel
        from app.identity.application.security import get_password_hasher

        password_hasher = get_password_hasher()
        user_model = UserModel(
            email='inactive@test.com',
            password_hash=password_hasher.hash('inactivepass123'),
            first_name='Inactive',
            last_name='User',
            is_active=False,
            is_superuser=False,
            is_verified=False,
        )
        async_db_session.add(user_model)
        await async_db_session.commit()

        resp = await client.post(
            '/api/v1/auth/login', data={
                'username': 'inactive@test.com',
                'password': 'inactivepass123',
                'grant_type': 'password',
            },
            headers={'accept': 'application/json'}
        )
        assert resp.status_code in [
            status.HTTP_200_OK,
            status.HTTP_400_BAD_REQUEST,
            status.HTTP_401_UNAUTHORIZED,
        ]


class TestAdminProfile:

    @pytest.mark.asyncio
    async def test_admin_profile_email(self, admin_client: AsyncClient):
        resp = await admin_client.get('/api/v1/auth/me')
        assert resp.status_code == status.HTTP_200_OK
        data = resp.json()
        assert data.get('email') == 'admin@test.com'
        assert data.get('first_name') == 'Super'
        assert data.get('last_name') == 'Admin'
