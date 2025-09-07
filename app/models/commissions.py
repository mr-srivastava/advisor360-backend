from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from app.models.base import EntityType


class Partner(BaseModel):
    """Partner model for commission-related operations"""

    id: str = Field(..., description="Partner ID")
    name: str = Field(..., description="Partner name")
    entityType: EntityType = Field(..., description="Entity type")
    createdAt: datetime = Field(..., description="Creation timestamp")


class Commission(BaseModel):
    """Commission model for commission-related operations"""

    id: str = Field(..., description="Commission ID")
    partnerId: str = Field(..., description="Partner ID")
    amount: float = Field(..., ge=0, description="Commission amount")
    month: str = Field(..., description="Month name (e.g., 'August')")
    year: str = Field(..., description="Year (e.g., '2025')")
    financialYear: str = Field(..., description="Financial year (e.g., 'FY25-26')")
    date: datetime = Field(..., description="Transaction date")
    description: Optional[str] = Field(None, description="Commission description")
    createdAt: datetime = Field(..., description="Creation timestamp")


class MonthlyAnalytics(BaseModel):
    """Monthly analytics model"""

    month: str = Field(..., description="Month name")
    year: str = Field(..., description="Year")
    total: float = Field(..., ge=0, description="Total amount")
    growth: float = Field(..., description="Growth percentage")
    commissionCount: int = Field(..., ge=0, description="Number of commissions")


class YearlyAnalytics(BaseModel):
    """Yearly analytics model"""

    financialYear: str = Field(..., description="Financial year")
    total: float = Field(..., ge=0, description="Total amount")
    growth: float = Field(..., description="Growth percentage")
    monthlyBreakdown: list[MonthlyAnalytics] = Field(
        ..., description="Monthly breakdown"
    )
