from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import String, Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.infra.base_model import Base
from app.core.infra.mixins import TimestampMixin

if TYPE_CHECKING:
    from .user_group_model import UserGroupModelM2M


class UserModel(Base, TimestampMixin):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    first_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    last_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    group_associations: Mapped[list["UserGroupModelM2M"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )
    groups: Mapped[list["GroupModel"]] = relationship(
        secondary="user_groups_m2m",
        back_populates="users",
        viewonly=True,
    )
