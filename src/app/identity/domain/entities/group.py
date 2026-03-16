from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from app.core.domain.entity_base import Entity
from app.core.utils.datetime_utils import utcnow
from app.identity.domain.value_objects import GroupID


@dataclass(kw_only=True)
class Group(Entity):
    id: GroupID
    name: str
    description: str | None = None
    is_system: bool = False
    created_at: datetime = field(default_factory=utcnow)
    updated_at: datetime = field(default_factory=utcnow)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": str(self.id),
            "name": self.name,
            "description": self.description,
            "is_system": self.is_system,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

    def update(self, name: str | None = None, description: str | None = None) -> None:
        if name is not None:
            self.name = name
        if description is not None:
            self.description = description
        self.updated_at = utcnow()
