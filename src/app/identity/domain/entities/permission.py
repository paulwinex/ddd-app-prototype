from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from app.core.domain.entity_base import Entity
from app.core.utils.datetime_utils import utcnow
from app.identity.domain.value_objects import PermissionID


@dataclass(kw_only=True)
class Permission(Entity):
    id: PermissionID
    name: str
    codename: str
    created_at: datetime = field(default_factory=utcnow)
    updated_at: datetime = field(default_factory=utcnow)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": str(self.id),
            "name": self.name,
            "codename": self.codename,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

    def update(self, name: str | None = None) -> None:
        if name is not None:
            self.name = name
        self.updated_at = utcnow()
