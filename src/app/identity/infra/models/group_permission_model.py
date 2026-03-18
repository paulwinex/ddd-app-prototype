from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.infra.base_model import Base

if TYPE_CHECKING:
    from .group_model import GroupModel
    from .permission_model import PermissionModel


class GroupPermissionModelM2M(Base):
    __tablename__ = "group_permissions_m2m"

    group_id: Mapped[str] = mapped_column(
        ForeignKey("groups.id", ondelete="CASCADE"),
        primary_key=True,
        index=True,
    )
    permission_id: Mapped[str] = mapped_column(
        ForeignKey("permissions.id", ondelete="CASCADE"),
        primary_key=True,
        index=True,
    )

    group: Mapped["GroupModel"] = relationship(back_populates="permission_associations")
    permission: Mapped["PermissionModel"] = relationship(back_populates="group_associations")
