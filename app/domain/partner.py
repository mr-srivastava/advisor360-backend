"""Partner domain model representing business partners in the commission system."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional


class EntityType(str, Enum):
    """Entity types for financial products"""

    MUTUAL_FUNDS = "Mutual Funds"
    LIFE_INSURANCE = "Life Insurance"
    HEALTH_INSURANCE = "Health Insurance"
    GENERAL_INSURANCE = "General Insurance"


@dataclass
class Partner:
    """Pure domain model representing a business partner.

    Contains core partner information and business rules for validation.
    """

    id: str
    name: str
    entity_type: EntityType
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None

    def __post_init__(self):
        """Validate partner data after initialization."""
        self._validate()

    def _validate(self):
        """Validate partner business rules."""
        if not self.id or not self.id.strip():
            raise ValueError("Partner ID cannot be empty")

        if not self.name or not self.name.strip():
            raise ValueError("Partner name cannot be empty")

        if len(self.name.strip()) < 2:
            raise ValueError("Partner name must be at least 2 characters long")

        if len(self.name.strip()) > 255:
            raise ValueError("Partner name cannot exceed 255 characters")

        if not isinstance(self.entity_type, EntityType):
            raise ValueError(f"Invalid entity type. Must be one of: {list(EntityType)}")

        if self.created_at > datetime.now():
            raise ValueError("Created date cannot be in the future")

        if self.updated_at and self.updated_at < self.created_at:
            raise ValueError("Updated date cannot be before created date")

    def update_name(self, new_name: str) -> "Partner":
        """Update partner name with validation."""
        if not new_name or not new_name.strip():
            raise ValueError("New name cannot be empty")

        return Partner(
            id=self.id,
            name=new_name.strip(),
            entity_type=self.entity_type,
            created_at=self.created_at,
            updated_at=datetime.now(),
        )

    def update_entity_type(self, new_entity_type: EntityType) -> "Partner":
        """Update partner entity type."""
        if not isinstance(new_entity_type, EntityType):
            raise ValueError(f"Invalid entity type. Must be one of: {list(EntityType)}")

        return Partner(
            id=self.id,
            name=self.name,
            entity_type=new_entity_type,
            created_at=self.created_at,
            updated_at=datetime.now(),
        )

    def is_active(self) -> bool:
        """Check if partner is active.
        For now, all partners are considered active.
        This can be extended with business rules later.
        """
        return True

    def get_display_name(self) -> str:
        """Get formatted display name for UI."""
        return f"{self.name} ({self.entity_type.value})"

    def to_dict(self) -> dict:
        """Convert to dictionary representation."""
        return {
            "id": self.id,
            "name": self.name,
            "entity_type": self.entity_type.value,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Partner":
        """Create Partner from dictionary."""
        return cls(
            id=data["id"],
            name=data["name"],
            entity_type=EntityType(data["entity_type"]),
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=(
                datetime.fromisoformat(data["updated_at"])
                if data.get("updated_at")
                else None
            ),
        )

    def __str__(self) -> str:
        return f"Partner(id={self.id}, name={self.name}, type={self.entity_type.value})"

    def __repr__(self) -> str:
        return (
            f"Partner(id='{self.id}', name='{self.name}', "
            f"entity_type={self.entity_type}, created_at={self.created_at})"
        )

    def __eq__(self, other) -> bool:
        if not isinstance(other, Partner):
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)
