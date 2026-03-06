import pytest

from app.core.settings import Settings, get_default_settings


@pytest.fixture(scope="session")
def test_settings() -> Settings:
    return get_default_settings(
        DB_HOST="celan_arch_prototype-db-testing",
        DB_NAME="test",
        DB_USER="test",
        DB_PASSWORD="test",
        ADMIN_EMAIL="admin@test.com",
        ADMIN_PASSWORD="admin@test.com",
        AUTH_ALLOW_SIMPLE_PASSWORDS=True,
    )
