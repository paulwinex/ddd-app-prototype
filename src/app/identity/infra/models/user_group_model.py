from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.infra.base_model import Base

if TYPE_CHECKING:
    from .user_model import UserModel
    from .group_model import GroupModel


class UserGroupModelM2M(Base):
    __tablename__ = "user_groups_m2m"

    user_id: Mapped[str] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
        index=True,
    )
    group_id: Mapped[str] = mapped_column(
        ForeignKey("groups.id", ondelete="CASCADE"),
        primary_key=True,
        index=True,
    )

    user: Mapped["UserModel"] = relationship(back_populates="group_associations")
    group: Mapped["GroupModel"] = relationship(back_populates="user_associations")
