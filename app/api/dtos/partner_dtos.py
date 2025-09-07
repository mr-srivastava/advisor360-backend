"""Partner DTOs for API request and response models."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, validator

from app.domain.partner import EntityType, Partner

from .common_dtos import BaseResponse, DataResponse, ListResponse, PaginatedResponse


# Request DTOs
class CreatePartnerRequest(BaseModel):
    """Request model for creating a new partner."""

    name: str = Field(..., description="Partner name", min_length=2, max_length=255)
    entity_type: str = Field(..., description="Entity type")

    @validator("name")
    def validate_name(cls, v):
        return v.strip()

    @validator("entity_type")
    def validate_entity_type(cls, v):
        try:
            EntityType(v)
            return v
        except ValueError:
            valid_types = [e.value for e in EntityType]
            raise ValueError(f"Invalid entity type. Must be one of: {valid_types}")

    def to_domain(self, partner_id: str) -> Partner:
        """Convert to domain model."""
        return Partner(
            id=partner_id, name=self.name, entity_type=EntityType(self.entity_type)
        )


class UpdatePartnerRequest(BaseModel):
    """Request model for updating an existing partner."""

    name: Optional[str] = Field(
        None, description="Partner name", min_length=2, max_length=255
    )
    entity_type: Optional[str] = Field(None, description="Entity type")

    @validator("name")
    def validate_name(cls, v):
        return v.strip() if v else v

    @validator("entity_type")
    def validate_entity_type(cls, v):
        if v is None:
            return v
        try:
            EntityType(v)
            return v
        except ValueError:
            valid_types = [e.value for e in EntityType]
            raise ValueError(f"Invalid entity type. Must be one of: {valid_types}")


class PartnerQueryParams(BaseModel):
    """Query parameters for partner endpoints."""

    entity_type: Optional[str] = Field(None, description="Filter by entity type")
    search: Optional[str] = Field(None, description="Search by partner name")
    active_only: bool = Field(True, description="Include only active partners")
    page: int = Field(1, description="Page number", ge=1)
    per_page: int = Field(10, description="Items per page", ge=1, le=100)

    @validator("entity_type")
    def validate_entity_type(cls, v):
        if v is None:
            return v
        try:
            EntityType(v)
            return v
        except ValueError:
            valid_types = [e.value for e in EntityType]
            raise ValueError(f"Invalid entity type. Must be one of: {valid_types}")


# Response DTOs
class PartnerResponse(BaseModel):
    """Response model for partner data."""

    id: str = Field(..., description="Partner ID")
    name: str = Field(..., description="Partner name")
    entity_type: str = Field(..., description="Entity type")
    display_name: str = Field(..., description="Formatted display name")
    is_active: bool = Field(..., description="Whether the partner is active")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")

    @classmethod
    def from_domain(cls, partner: Partner) -> "PartnerResponse":
        """Create response DTO from domain model."""
        return cls(
            id=partner.id,
            name=partner.name,
            entity_type=partner.entity_type.value,
            display_name=partner.get_display_name(),
            is_active=partner.is_active(),
            created_at=partner.created_at,
            updated_at=partner.updated_at,
        )


class EntityTypeResponse(BaseModel):
    """Response model for entity type data."""

    value: str = Field(..., description="Entity type value")
    label: str = Field(..., description="Human-readable label")

    @classmethod
    def from_enum(cls, entity_type: EntityType) -> "EntityTypeResponse":
        """Create response DTO from enum."""
        return cls(value=entity_type.value, label=entity_type.value)


class PartnerSummary(BaseModel):
    """Summary information for partner aggregations."""

    total_partners: int = Field(..., description="Total number of partners")
    active_partners: int = Field(..., description="Number of active partners")
    entity_type_breakdown: dict = Field(..., description="Breakdown by entity type")


class PartnerDetailResponse(DataResponse[PartnerResponse]):
    """Response for single partner detail."""

    pass


class PartnerListResponse(ListResponse[PartnerResponse]):
    """Response for partner list."""

    summary: Optional[PartnerSummary] = Field(None, description="Summary statistics")


class PartnerPaginatedResponse(PaginatedResponse[PartnerResponse]):
    """Paginated response for partner list."""

    summary: Optional[PartnerSummary] = Field(None, description="Summary statistics")


class EntityTypesResponse(ListResponse[EntityTypeResponse]):
    """Response for entity types list."""

    pass


# Analytics DTOs
class PartnerPerformanceData(BaseModel):
    """Partner performance analytics data."""

    partner_id: str = Field(..., description="Partner ID")
    partner_name: str = Field(..., description="Partner name")
    entity_type: str = Field(..., description="Entity type")
    total_commissions: float = Field(..., description="Total commission amount")
    commission_count: int = Field(..., description="Number of commissions")
    average_commission: float = Field(..., description="Average commission amount")
    last_commission_date: Optional[datetime] = Field(
        None, description="Date of last commission"
    )
    performance_rank: int = Field(..., description="Performance ranking")


class PartnerAnalyticsResponse(BaseResponse):
    """Response for partner analytics."""

    performance_data: list[PartnerPerformanceData] = Field(
        ..., description="Partner performance data"
    )
    summary: PartnerSummary = Field(..., description="Overall summary")


# Mapping utilities
class PartnerMapper:
    """Utility class for mapping between domain models and DTOs."""

    @staticmethod
    def to_response(partner: Partner) -> PartnerResponse:
        """Convert domain model to response DTO."""
        return PartnerResponse.from_domain(partner)

    @staticmethod
    def to_response_list(partners: list[Partner]) -> list[PartnerResponse]:
        """Convert list of domain models to response DTOs."""
        return [PartnerResponse.from_domain(partner) for partner in partners]

    @staticmethod
    def create_summary(partners: list[Partner]) -> PartnerSummary:
        """Create summary from list of partners."""
        total_partners = len(partners)
        active_partners = sum(1 for p in partners if p.is_active())

        entity_type_breakdown = {}
        for partner in partners:
            entity_type = partner.entity_type.value
            entity_type_breakdown[entity_type] = (
                entity_type_breakdown.get(entity_type, 0) + 1
            )

        return PartnerSummary(
            total_partners=total_partners,
            active_partners=active_partners,
            entity_type_breakdown=entity_type_breakdown,
        )

    @staticmethod
    def get_entity_types() -> list[EntityTypeResponse]:
        """Get all available entity types."""
        return [EntityTypeResponse.from_enum(entity_type) for entity_type in EntityType]
