from functools import cached_property, cache

from pydantic import Field, SecretStr, PostgresDsn, EmailStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class AuthSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="APP_AUTH_")

    JWT_SECRET: SecretStr
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_EXPIRE_SECONDS: int = 900
    JWT_REFRESH_EXPIRE_SECONDS: int = 604800
    ALLOW_SIMPLE_PASSWORDS: bool = False


class DatabaseSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="APP_DB_")

    HOST: str = "localhost"
    PORT: int = 5432
    NAME: str = "app_db"
    USER: str = "app_user"
    PASSWORD: SecretStr = SecretStr("password")

    @cached_property
    def dsn(self) -> str:
        return str(
            PostgresDsn.build(
                scheme="postgresql+asyncpg",
                username=self.USER,
                password=self.PASSWORD.get_secret_value(),
                host=self.HOST,
                port=self.PORT,
                path=self.NAME,
            )
        )


class RedisSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="APP_REDIS_")

    HOST: str = "localhost"
    PORT: int = 6379
    DB: int = 0

    @cached_property
    def dsn(self) -> str:
        return f"redis://{self.HOST}:{self.PORT}/{self.DB}"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="APP_",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    NAME: str = Field(default="NoName")
    DEBUG: bool = False
    DEFAULT_PORT: int = 8000
    DEFAULT_HOST: str = "0.0.0.0"
    DOMAIN: str = "http://localhost:8000"

    # sub-settings
    AUTH: AuthSettings = Field(default_factory=AuthSettings)
    DB: DatabaseSettings = Field(default_factory=DatabaseSettings)
    REDIS: RedisSettings = Field(default_factory=RedisSettings)

    # default super admin
    ADMIN_EMAIL: EmailStr
    ADMIN_PASSWORD: SecretStr


@cache
def get_default_settings() -> Settings:
    return Settings()
