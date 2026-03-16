from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.infra.base_model import Base
from app.core.infra.mixins import TimestampMixin

if TYPE_CHECKING:
    from .group_model import GroupModel
    from .group_permission_model import GroupPermissionModelM2M


class PermissionModel(TimestampMixin, Base):
    __tablename__ = "permissions"

    name: Mapped[str] = mapped_column(nullable=False)
    codename: Mapped[str] = mapped_column(unique=True, nullable=False, index=True)

    group_associations: Mapped[list["GroupPermissionModelM2M"]] = relationship(
        back_populates="permission",
        cascade="all, delete-orphan",
    )
    groups: Mapped[list["GroupModel"]] = relationship(
        secondary="group_permissions_m2m",
        back_populates="permissions",
        viewonly=True,
    )
