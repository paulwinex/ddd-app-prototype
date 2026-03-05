from dataclasses import dataclass, field
from datetime import datetime

from app.core.utils.datetime_utils import utcnow
from app.identity.domain.value_objects import UserID, EmailVO, PasswordVO


@dataclass(kw_only=True)
class User:
    id: UserID
    email: EmailVO
    password: PasswordVO
    first_name: str | None = None
    last_name: str | None = None
    is_active: bool = True
    is_superuser: bool = False
    is_verified: bool = False
    created_at: datetime = field(default_factory=utcnow)
    updated_at: datetime = field(default_factory=utcnow)
    last_login_at: datetime | None = None

    def update_last_login(self) -> None:
        self.last_login_at = utcnow()
        self.updated_at = utcnow()

    def activate(self) -> None:
        self.is_active = True
        self.updated_at = utcnow()

    def deactivate(self) -> None:
        self.is_active = False
        self.updated_at = utcnow()

    def verify(self) -> None:
        self.is_verified = True
        self.updated_at = utcnow()

    def update(
        self,
        first_name: str | None = None,
        last_name: str | None = None,
    ) -> None:
        if first_name is not None:
            self.first_name = first_name
        if last_name is not None:
            self.last_name = last_name
        self.updated_at = utcnow()

    def change_password(self, new_password: str | PasswordVO) -> None:
        if isinstance(new_password, str):
            new_password = PasswordVO(new_password)
        self.password = new_password
        self.updated_at = utcnow()
