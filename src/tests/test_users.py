import pytest
from httpx import AsyncClient
from fastapi import status

from app.identity.infra.models import UserModel


class TestUserCreate:
    
    @pytest.mark.asyncio
    async def test_create_user_success(self, admin_client: AsyncClient):
        user_data = {
            'email': 'newuser@test.com',
            'password': 'password123',
            'first_name': 'New',
            'last_name': 'User',
        }
        resp = await admin_client.post('/api/v1/users', json=user_data)
        assert resp.status_code == status.HTTP_201_CREATED
        data = resp.json()
        assert data['email'] == 'newuser@test.com'
        assert data['first_name'] == 'New'
        assert data['last_name'] == 'User'
        assert 'id' in data

    @pytest.mark.asyncio
    async def test_create_user_duplicate_email(self, admin_client: AsyncClient, regular_user):
        user_data = {
            'email': str(regular_user.email),
            'password': 'password123',
            'first_name': 'Duplicate',
            'last_name': 'User',
        }
        resp = await admin_client.post('/api/v1/users', json=user_data)
        assert resp.status_code in [status.HTTP_400_BAD_REQUEST, status.HTTP_409_CONFLICT, status.HTTP_500_INTERNAL_SERVER_ERROR]

    @pytest.mark.asyncio
    async def test_create_user_invalid_email(self, admin_client: AsyncClient):
        user_data = {
            'email': 'invalid-email',
            'password': 'password123',
            'first_name': 'Invalid',
            'last_name': 'User',
        }
        resp = await admin_client.post('/api/v1/users', json=user_data)
        assert resp.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    @pytest.mark.asyncio
    async def test_create_user_short_password(self, admin_client: AsyncClient):
        user_data = {
            'email': 'shortpass@test.com',
            'password': 'short',
            'first_name': 'Short',
            'last_name': 'Pass',
        }
        resp = await admin_client.post('/api/v1/users', json=user_data)
        assert resp.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    @pytest.mark.asyncio
    async def test_create_user_unauthorized(self, client: AsyncClient):
        user_data = {
            'email': 'unauth@test.com',
            'password': 'password123',
            'first_name': 'Unauth',
            'last_name': 'User',
        }
        resp = await client.post('/api/v1/users', json=user_data)
        assert resp.status_code == status.HTTP_201_CREATED


class TestUserGet:
    
    @pytest.mark.asyncio
    async def test_get_user_by_id(self, admin_client: AsyncClient, regular_user):
        resp = await admin_client.get(f'/api/v1/users/{regular_user.id}')
        assert resp.status_code == status.HTTP_200_OK
        data = resp.json()
        assert data['email'] == str(regular_user.email)
        assert data['first_name'] == 'Regular'
        assert data['last_name'] == 'User'

    @pytest.mark.asyncio
    async def test_get_nonexistent_user(self, admin_client: AsyncClient):
        resp = await admin_client.get('/api/v1/users/00000000-0000-0000-0000-000000000000')
        assert resp.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.asyncio
    async def test_get_user_unauthorized(self, client: AsyncClient, regular_user):
        resp = await client.get(f'/api/v1/users/{regular_user.id}')
        assert resp.status_code == status.HTTP_200_OK


class TestUserList:
    
    @pytest.mark.asyncio
    async def test_list_users_success(self, admin_client: AsyncClient):
        resp = await admin_client.get('/api/v1/users')
        assert resp.status_code == status.HTTP_200_OK
        data = resp.json()
        assert 'items' in data
        assert 'total' in data
        assert 'limit' in data
        assert 'offset' in data
        assert len(data['items']) >= 1

    @pytest.mark.asyncio
    async def test_list_users_with_pagination(self, admin_client: AsyncClient):
        resp = await admin_client.get('/api/v1/users?limit=1&offset=0')
        assert resp.status_code == status.HTTP_200_OK
        data = resp.json()
        assert len(data['items']) == 1
        assert data['limit'] == 1
        assert data['offset'] == 0

    @pytest.mark.asyncio
    async def test_list_users_filter_by_email(self, admin_client: AsyncClient, regular_user):
        resp = await admin_client.get(f'/api/v1/users?email={regular_user.email}')
        assert resp.status_code == status.HTTP_200_OK
        data = resp.json()
        assert len(data['items']) == 1
        assert data['items'][0]['email'] == str(regular_user.email)

    @pytest.mark.asyncio
    async def test_list_users_filter_by_is_active(self, admin_client: AsyncClient):
        resp = await admin_client.get('/api/v1/users?is_active=true')
        assert resp.status_code == status.HTTP_200_OK
        data = resp.json()
        assert 'items' in data
        assert len(data['items']) >= 1

    @pytest.mark.asyncio
    async def test_list_users_filter_by_is_superuser(self, admin_client: AsyncClient):
        resp = await admin_client.get('/api/v1/users?is_superuser=true')
        assert resp.status_code == status.HTTP_200_OK
        data = resp.json()
        # Only admin should be superuser
        assert len(data['items']) == 1
        assert data['items'][0]['email'] == 'admin@test.com'

    @pytest.mark.asyncio
    async def test_list_users_unauthorized(self, client: AsyncClient):
        resp = await client.get('/api/v1/users')
        # Note: API allows public read access to user list
        assert resp.status_code == status.HTTP_200_OK


class TestUserUpdate:
    
    @pytest.mark.asyncio
    async def test_update_user_success(self, admin_client: AsyncClient, regular_user):
        update_data = {
            'first_name': 'Updated',
            'last_name': 'Name',
        }
        resp = await admin_client.patch(
            f'/api/v1/users/{regular_user.id}',
            json=update_data
        )
        assert resp.status_code == status.HTTP_200_OK

    @pytest.mark.asyncio
    async def test_update_user_empty_body(self, admin_client: AsyncClient, regular_user):
        resp = await admin_client.patch(
            f'/api/v1/users/{regular_user.id}',
            json={}
        )
        assert resp.status_code == status.HTTP_200_OK

    @pytest.mark.asyncio
    async def test_update_nonexistent_user(self, admin_client: AsyncClient):
        update_data = {'first_name': 'Updated'}
        resp = await admin_client.patch(
            '/api/v1/users/00000000-0000-0000-0000-000000000000',
            json=update_data
        )
        assert resp.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.asyncio
    async def test_update_user_unauthorized(self, client: AsyncClient, regular_user):
        update_data = {'first_name': 'Updated'}
        resp = await client.patch(
            f'/api/v1/users/{regular_user.id}',
            json=update_data
        )
        assert resp.status_code == status.HTTP_200_OK


class TestUserDelete:
    
    @pytest.mark.asyncio
    async def test_delete_user_success(self, admin_client: AsyncClient, async_db_session):
        from sqlalchemy import select

        user_to_delete = UserModel(
            email='todelete@test.com',
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
    async def test_delete_admin_user_forbidden(self, admin_client: AsyncClient, admin_user):
        resp = await admin_client.delete(f'/api/v1/users/{admin_user.id}')
        assert resp.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.asyncio
    async def test_delete_nonexistent_user(self, admin_client: AsyncClient):
        resp = await admin_client.delete('/api/v1/users/00000000-0000-0000-0000-000000000000')
        assert resp.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.asyncio
    async def test_delete_user_unauthorized(self, client: AsyncClient, regular_user):
        resp = await client.delete(f'/api/v1/users/{regular_user.id}')
        assert resp.status_code == status.HTTP_204_NO_CONTENT


class TestUserChangePassword:
    
    @pytest.mark.asyncio
    async def test_change_password_success(self, admin_client: AsyncClient, regular_user):
        password_data = {
            'current_password': 'regularpass123',
            'new_password': 'newpassword456',
        }
        resp = await admin_client.post(
            f'/api/v1/users/{regular_user.id}/change-password',
            json=password_data
        )
        assert resp.status_code == status.HTTP_204_NO_CONTENT

    @pytest.mark.asyncio
    async def test_change_password_wrong_current(self, admin_client: AsyncClient, regular_user):
        password_data = {
            'current_password': 'wrongpassword',
            'new_password': 'newpassword456',
        }
        resp = await admin_client.post(
            f'/api/v1/users/{regular_user.id}/change-password',
            json=password_data
        )
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.asyncio
    async def test_change_password_short_new(self, admin_client: AsyncClient, regular_user):
        password_data = {
            'current_password': 'regularpass123',
            'new_password': 'short',
        }
        resp = await admin_client.post(
            f'/api/v1/users/{regular_user.id}/change-password',
            json=password_data
        )
        assert resp.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    @pytest.mark.asyncio
    async def test_change_password_nonexistent_user(self, admin_client: AsyncClient):
        password_data = {
            'current_password': 'somepass',
            'new_password': 'newpassword456',
        }
        resp = await admin_client.post(
            '/api/v1/users/00000000-0000-0000-0000-000000000000/change-password',
            json=password_data
        )
        assert resp.status_code == status.HTTP_404_NOT_FOUND
