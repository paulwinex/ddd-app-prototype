from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.infra.base_model import Base
from app.core.infra.mixins import SoftDeleteMixin, AuditMixin

if TYPE_CHECKING:
    from .user_model import UserModel
    from .user_group_model import UserGroupModelM2M
    from .group_permission_model import GroupPermissionModelM2M
    from .permission_model import PermissionModel


class GroupModel(SoftDeleteMixin, AuditMixin, Base):
    __tablename__ = "groups"

    name: Mapped[str] = mapped_column(unique=True, nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(String(2048))
    is_system: Mapped[bool] = mapped_column(default=False, nullable=False)

    user_associations: Mapped[list["UserGroupModelM2M"]] = relationship(
        back_populates="group",
        cascade="all, delete-orphan",
    )
    users: Mapped[list["UserModel"]] = relationship(
        secondary="user_groups_m2m",
        back_populates="groups",
        viewonly=True,
    )

    permission_associations: Mapped[list["GroupPermissionModelM2M"]] = relationship(
        back_populates="group",
        cascade="all, delete-orphan",
    )
    permissions: Mapped[list["PermissionModel"]] = relationship(
        secondary="group_permissions_m2m",
        back_populates="groups",
        viewonly=True,
    )
