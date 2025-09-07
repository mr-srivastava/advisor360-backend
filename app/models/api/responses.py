"""Response models for API endpoints"""

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field

from app.models.base import BaseResponse


# Dashboard Response Models
class StatCard(BaseModel):
    """Individual stat card for dashboard"""

    id: str = Field(..., description="Unique identifier for the stat")
    title: str = Field(..., description="Title of the stat")
    value: float | str = Field(..., description="Value of the stat")
    subtitle: str = Field(..., description="Subtitle or description")
    icon: str = Field(..., description="Icon identifier")
    trend: Optional[dict[str, Any]] = Field(None, description="Trend data if available")


class TrendData(BaseModel):
    """Trend data for statistics"""

    value: str = Field(..., description="Trend value")
    isPositive: bool = Field(..., description="Whether the trend is positive")


class DashboardOverviewResponse(BaseResponse):
    """Response for dashboard overview"""

    data: dict[str, list[StatCard]] = Field(
        ..., description="Dashboard data containing stats"
    )


class FYMetricsData(BaseModel):
    """Financial year metrics data"""

    selectedFY: str = Field(..., description="Selected financial year")
    currentYearTotal: float = Field(..., description="Total for current year")
    yoyGrowth: float = Field(..., description="Year over year growth percentage")
    commissionCount: int = Field(..., description="Number of commissions")


class FYMetricsResponse(BaseResponse):
    """Response for financial year metrics"""

    data: FYMetricsData = Field(..., description="Financial year metrics data")


class MonthlyGrowthData(BaseModel):
    """Monthly growth data"""

    month: str = Field(..., description="Month name")
    total: float = Field(..., description="Total for the month")
    growth: Optional[float] = Field(None, description="Growth percentage")


class EntityPerformanceData(BaseModel):
    """Entity performance data"""

    entity_id: str = Field(..., description="Entity ID")
    entity_name: str = Field(..., description="Entity name")
    total: float = Field(..., description="Total amount")
    percentage: float = Field(..., description="Percentage of total")


class PerformanceMetricsData(BaseModel):
    """Performance metrics data"""

    monthlyGrowth: list[MonthlyGrowthData] = Field(
        ..., description="Monthly growth data"
    )
    entityPerformance: list[EntityPerformanceData] = Field(
        ..., description="Entity performance data"
    )


class PerformanceMetricsResponse(BaseResponse):
    """Response for performance metrics"""

    data: PerformanceMetricsData = Field(..., description="Performance metrics data")


class RecentActivityData(BaseModel):
    """Recent activity data"""

    recent_commissions: list[dict[str, Any]] = Field(
        ..., description="Recent commission records"
    )
    monthly_commissions: list[dict[str, Any]] = Field(
        ..., description="Monthly commission summaries"
    )


class RecentActivityResponse(BaseResponse):
    """Response for recent activities"""

    data: RecentActivityData = Field(..., description="Recent activities data")


# Partner Response Models
class PartnerResponse(BaseModel):
    """Individual partner response"""

    id: str = Field(..., description="Partner ID")
    name: str = Field(..., description="Partner name")
    entity_type: Optional[str] = Field(None, description="Entity type name")
    created_at: datetime = Field(..., description="Creation timestamp")


class PartnersListData(BaseModel):
    """Partners list data"""

    partners: list[PartnerResponse] = Field(..., description="List of partners")


class PartnersListResponse(BaseResponse):
    """Response for partners list"""

    data: PartnersListData = Field(..., description="Partners data")


class EntityTypeResponse(BaseModel):
    """Entity type response"""

    id: str = Field(..., description="Entity type ID")
    name: str = Field(..., description="Entity type name")


class EntityTypesData(BaseModel):
    """Entity types data"""

    entity_types: list[EntityTypeResponse] = Field(
        ..., description="List of entity types"
    )


class EntityTypesResponse(BaseResponse):
    """Response for entity types list"""

    data: EntityTypesData = Field(..., description="Entity types data")


# Commission Response Models
class CommissionResponse(BaseModel):
    """Individual commission response"""

    id: str = Field(..., description="Commission ID")
    partnerId: str = Field(..., description="Partner ID")
    amount: float = Field(..., description="Commission amount")
    month: str = Field(..., description="Month name")
    year: str = Field(..., description="Year")
    financialYear: str = Field(..., description="Financial year")
    date: datetime = Field(..., description="Transaction date")
    description: Optional[str] = Field(None, description="Commission description")
    createdAt: datetime = Field(..., description="Creation timestamp")
    partner: Optional[dict[str, Any]] = Field(..., description="Partner details")


class CommissionsListData(BaseModel):
    """Commissions list data"""

    commissions: list[CommissionResponse] = Field(
        ..., description="List of commissions"
    )


class CommissionsListResponse(BaseResponse):
    """Response for commissions list"""

    data: CommissionsListData = Field(..., description="Commissions data")


# Common Response Models
class FinancialYearsData(BaseModel):
    """Financial years data"""

    financial_years: list[str] = Field(
        ..., description="List of available financial years"
    )


class FinancialYearsResponse(BaseResponse):
    """Response for available financial years"""

    data: FinancialYearsData = Field(..., description="Financial years data")
