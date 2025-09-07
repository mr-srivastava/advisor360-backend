"""Database model for Partner entity mapping."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from ...domain.partner import EntityType, Partner


class PartnerModel(BaseModel):
    """Database model for partners that maps between domain models and database schema.

    This model handles the conversion between the rich domain model and the
    flat database representation used by Supabase.
    """

    id: str = Field(..., description="Partner unique identifier")
    name: str = Field(..., min_length=1, max_length=255, description="Partner name")
    type_id: str = Field(..., description="Entity type ID (foreign key)")
    created_at: datetime = Field(
        default_factory=datetime.now, description="Creation timestamp"
    )
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")

    # Additional fields that might come from joined queries
    entity_type_name: Optional[str] = Field(
        None, description="Entity type name from join"
    )

    class Config:
        from_attributes = True
        json_encoders = {datetime: lambda v: v.isoformat()}

    def to_domain(self) -> Partner:
        """Convert database model to domain model.

        Returns:
            Partner domain model instance
        """
        # Map entity type name to enum
        entity_type = self._map_entity_type_name_to_enum(
            self.entity_type_name or self._get_entity_type_from_id(self.type_id)
        )

        return Partner(
            id=self.id,
            name=self.name,
            entity_type=entity_type,
            created_at=self.created_at,
            updated_at=self.updated_at,
        )

    @classmethod
    def from_domain(cls, partner: Partner) -> "PartnerModel":
        """Create database model from domain model.

        Args:
            partner: Partner domain model

        Returns:
            PartnerModel instance
        """
        type_id = cls._map_entity_type_enum_to_id(partner.entity_type)

        return cls(
            id=partner.id,
            name=partner.name,
            type_id=type_id,
            created_at=partner.created_at,
            updated_at=partner.updated_at,
            entity_type_name=partner.entity_type.value,
        )

    @classmethod
    def from_database_row(cls, row: dict) -> "PartnerModel":
        """Create model from raw database row.

        Args:
            row: Raw database row dictionary

        Returns:
            PartnerModel instance
        """
        # Handle different possible datetime formats
        created_at_value = row.get("created_at")
        if isinstance(created_at_value, str):
            created_at = datetime.fromisoformat(created_at_value.replace("Z", "+00:00"))
        elif isinstance(created_at_value, datetime):
            created_at = created_at_value
        else:
            created_at = datetime.now()

        updated_at_value = row.get("updated_at")
        updated_at = None
        if updated_at_value:
            if isinstance(updated_at_value, str):
                updated_at = datetime.fromisoformat(
                    updated_at_value.replace("Z", "+00:00")
                )
            elif isinstance(updated_at_value, datetime):
                updated_at = updated_at_value

        return cls(
            id=row["id"],
            name=row["name"],
            type_id=row["type_id"],
            created_at=created_at,
            updated_at=updated_at,
            entity_type_name=row.get("entity_type_name")
            or row.get("name"),  # from entity_types join
        )

    def to_database_dict(self) -> dict:
        """Convert to dictionary for database operations.

        Returns:
            Dictionary suitable for database insertion/update
        """
        data = {
            "id": self.id,
            "name": self.name,
            "type_id": self.type_id,
            "created_at": self.created_at.isoformat(),
        }

        if self.updated_at is not None:
            data["updated_at"] = self.updated_at.isoformat()

        return data

    @staticmethod
    def _map_entity_type_name_to_enum(type_name: str) -> EntityType:
        """Map database entity type name to domain enum."""
        type_mapping = {
            "Mutual Funds": EntityType.MUTUAL_FUNDS,
            "Life Insurance": EntityType.LIFE_INSURANCE,
            "Health Insurance": EntityType.HEALTH_INSURANCE,
            "General Insurance": EntityType.GENERAL_INSURANCE,
        }

        if type_name in type_mapping:
            return type_mapping[type_name]

        # Fallback: try to match by enum value
        for entity_type in EntityType:
            if entity_type.value == type_name:
                return entity_type

        # Default fallback
        return EntityType.MUTUAL_FUNDS

    @staticmethod
    def _map_entity_type_enum_to_id(entity_type: EntityType) -> str:
        """Map domain entity type enum to database type ID."""
        # This mapping should ideally come from a configuration or database lookup
        # For now, we'll use a simple mapping based on common patterns
        type_id_mapping = {
            EntityType.MUTUAL_FUNDS: "1",
            EntityType.LIFE_INSURANCE: "2",
            EntityType.HEALTH_INSURANCE: "3",
            EntityType.GENERAL_INSURANCE: "4",
        }

        return type_id_mapping.get(entity_type, "1")

    @staticmethod
    def _get_entity_type_from_id(type_id: str) -> str:
        """Get entity type name from type ID."""
        id_to_name_mapping = {
            "1": "Mutual Funds",
            "2": "Life Insurance",
            "3": "Health Insurance",
            "4": "General Insurance",
        }

        return id_to_name_mapping.get(type_id, "Mutual Funds")

    def get_display_name(self) -> str:
        """Get formatted display name for UI."""
        entity_type_name = self.entity_type_name or self._get_entity_type_from_id(
            self.type_id
        )
        return f"{self.name} ({entity_type_name})"
